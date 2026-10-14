"""Probe official resources without exposing authentication values."""
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URLS = {
    "requested_eg2_metadata": "https://huggingface.co/api/models/google/embeddinggemma-2",
    "requested_eg2_model_card": "https://huggingface.co/google/embeddinggemma-2/raw/main/README.md",
    "google_gemini_models": "https://ai.google.dev/gemini-api/docs/models",
    "google_decision_maker": "https://ai.google.dev/edge/mediapipe/solutions/text/decision_maker",
    "nli_fallback_metadata": "https://huggingface.co/api/models/MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
}


def main():
    results = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "credentials_present": {
        name: bool(os.environ.get(name)) for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "HF_TOKEN")}, "resources": {}}
    for key, url in URLS.items():
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                body = response.read()
                result = {"url": url, "http_status": response.status, "bytes": len(body)}
                if "metadata" in key:
                    metadata = json.loads(body)
                    result.update(model_id=metadata.get("id"), revision=metadata.get("sha"), gated=metadata.get("gated"))
        except Exception as exc:
            result = {"url": url, "error": str(exc), "error_type": type(exc).__name__}
        results["resources"][key] = result
    Path("results").mkdir(exist_ok=True)
    Path("results/preflight.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
