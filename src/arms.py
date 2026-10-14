"""Scores are larger for more likely status change. Imports are lazy."""
import difflib
import numpy as np


def score_a(old_text, new_text):
    edits = sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in
                difflib.SequenceMatcher(None, old_text, new_text, autojunk=False).get_opcodes() if tag != "equal")
    return edits / max(len(old_text), 1)


def cosine_distance(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0 or not np.isfinite(denom):
        raise ValueError("Invalid/zero embedding")
    return float(np.clip(1 - np.dot(a, b) / denom, 0, 2))


def probabilities(vector, labels, temperature):
    if temperature <= 0:
        raise ValueError("Temperature must be positive")
    cos = np.array([1 - cosine_distance(vector, label) for label in labels])
    logits = (cos - cos.max()) / temperature
    exp = np.exp(logits)
    return exp / exp.sum(), int(cos.argmax())


def verified(config):
    if not all(config.get(k) for k in ("verified", "model_id", "revision", "official_source")):
        raise ValueError("Model ID, immutable revision and official usage must be verified before model loading")


class EmbeddingArms:
    def __init__(self, config, labels):
        verified(config)
        for key in ("document_template", "classification_template", "search_query_template"):
            if not config.get(key) or "{text}" not in config[key]:
                raise ValueError(f"Verify exact task prefix/template: {key}")
        import torch
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(config["model_id"], revision=config["revision"], device="cpu",
                                         trust_remote_code=False, model_kwargs={"torch_dtype": torch.float32},
                                         config_kwargs=config.get("config_kwargs", {}))
        if config.get("max_seq_length"):
            self.model.max_seq_length = config["max_seq_length"]
        self.model.eval()
        self.config, self.label_texts, self.cache, self.labels = config, labels, {}, {}

    def encode(self, texts, template, batch_size=None):
        formatted = [template.format(text=t) for t in texts]
        # Reject truncation: silently dropping the new blocker invalidates this experiment.
        lengths = self.model.tokenizer(formatted, add_special_tokens=True, truncation=False, padding=False)["input_ids"]
        if any(len(ids) > self.model.max_seq_length for ids in lengths):
            raise ValueError("Input exceeds model context; revise paragraph selection before scoring")
        output = self.model.encode(formatted, batch_size=batch_size or self.config["batch_size"],
                                   convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False,
                                   prompt="")
        if output.shape[1] != 768:
            raise ValueError(f"Protocol requires 768 dimensions, got {output.shape[1]}; do not relabel another model as EG2")
        return output

    def prepare(self, rows):
        texts = sorted({p[k] for p in rows for k in ("old_text", "new_text")})
        vectors = self.encode(texts, self.config["document_template"])
        self.cache = dict(zip(texts, vectors))
        for lang, texts in self.label_texts.items():
            for prefix in ("classification", "search_query"):
                self.labels[lang, prefix] = self.encode(texts, self.config[f"{prefix}_template"])

    def score_b(self, old_text, new_text, dimensions=768):
        return cosine_distance(self.cache[old_text][:dimensions], self.cache[new_text][:dimensions])

    def score_c(self, old_text, new_text, lang, prefix):
        labels = self.labels[lang, prefix]
        old_p, old_max = probabilities(self.cache[old_text], labels, self.config["temperature"])
        new_p, new_max = probabilities(self.cache[new_text], labels, self.config["temperature"])
        return cosine_distance(old_p, new_p), int(old_max != new_max)

    def noise(self, rows, seed):
        selected = [p for p in rows if p["category"] == "T0"]
        if not selected:
            raise ValueError("Q6 requires T0 before other embedding scores")
        texts = [p["old_text"] for p in selected]
        baseline = self.encode(texts, self.config["document_template"])
        rng = np.random.default_rng(seed)
        output = []
        for run, batch in enumerate((1, 8, 32), 1):
            order = rng.permutation(len(texts))
            vectors = self.encode([texts[i] for i in order], self.config["document_template"], batch)
            restored = np.empty_like(vectors)
            restored[order] = vectors
            distances = [cosine_distance(a, b) for a, b in zip(baseline, restored)]
            output.append({"run": run, "batch_size": batch, "n": len(texts),
                           "mean": float(np.mean(distances)), "std": float(np.std(distances)),
                           "p95": float(np.percentile(distances, 95)), "max": float(np.max(distances)),
                           "distances": distances})
        return output


class NLIArm:
    """D is explicitly an NLI substitute, never a Decision Maker result."""
    def __init__(self, config):
        verified(config)
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(config["model_id"], revision=config["revision"], trust_remote_code=False)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            config["model_id"], revision=config["revision"], trust_remote_code=False, torch_dtype=torch.float32)
        self.model.eval()
        mapping = self.model.config.id2label
        indices = [int(i) for i, label in mapping.items() if str(label).lower() == "contradiction"]
        if len(indices) != 1 or len(mapping) != 3:
            raise ValueError("Official model config must identify a three-way NLI contradiction class")
        self.contradiction = indices[0]

    def score(self, old_text, new_text):
        return self.score_batch([(old_text, new_text)])[0]

    def score_batch(self, pairs):
        premises = [t for old, new in pairs for t in (old, new)]
        hypotheses = [t for old, new in pairs for t in (new, old)]
        x = self.tokenizer(premises, hypotheses, padding=True, truncation=False, return_tensors="pt")
        limit = min(self.tokenizer.model_max_length, getattr(self.model.config, "max_position_embeddings", 512))
        if x["input_ids"].shape[1] > limit:
            raise ValueError("NLI pair exceeds context; no silent truncation")
        with self.torch.inference_mode():
            probs = self.model(**x).logits.softmax(-1)[:, self.contradiction]
        return probs.reshape(-1, 2).max(dim=1).values.tolist()


class LLMArm:
    def __init__(self, config):
        from .llm import Gemini
        self.client = Gemini(config)

    def score(self, old_text, new_text):
        from .llm import state_judgment
        result = state_judgment(self.client, old_text, new_text, "arm-E")
        if result["changed"] is None:
            return None, result["reason"]
        return float(result["changed"]), result["reason"]
