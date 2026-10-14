"""Thin bridge to pinned jevlike; prompt and probability reader remain upstream."""
import importlib
import subprocess
import sys
from pathlib import Path

class JArm:
    def __init__(self, plan, config, model_size, base_url, repo='/workspace/jevlike'):
        if model_size not in plan['models']:raise ValueError('Unregistered model size')
        repo=Path(repo).resolve()
        revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
        if revision!=plan['jevlike_revision']:raise ValueError('jevlike revision differs from frozen plan')
        for file in ('decide/prompt.py','decide/client.py','decide/labels.py'):
            expected=subprocess.check_output(['git','show',f'HEAD:{file}'],cwd=repo)
            if (repo/file).read_bytes()!=expected:raise ValueError(f'jevlike source modified: {file}')
        sys.path.insert(0,str(repo))
        prompt=importlib.import_module('decide.prompt');client=importlib.import_module('decide.client');labels=importlib.import_module('decide.labels')
        self.renderer=prompt.TemplateRenderer(base_url)
        self.read=client.read_option_probs;self.system={'zh':prompt.SYSTEM,'en':prompt.SYSTEM_EN}
        self.label_ids=labels.check_labels_llama(base_url,letters='ABCD')
        self.plan,self.config,self.model_size,self.url=plan,config,model_size,base_url
        import requests
        self.session=requests.Session();self.session.trust_env=False

    def score_j(self, new_text, lang, mode='single', old_text=None):
        if mode in ('single','docset'):
            question={'instructions':self.plan['single_instructions'][lang],
                      'options':dict(zip('ABCD',self.config['labels_alt'][lang]))}
            state=new_text;letters=list('ABCD')
        elif mode=='paired':
            if old_text is None:raise ValueError('Paired J needs old text')
            question={'instructions':self.plan['paired_instructions'][lang], 'options':self.plan['paired_options'][lang]}
            state=f'OLD / 舊版本:\n{old_text}\n\nNEW / 新版本:\n{new_text}';letters=list('AB')
        else:raise ValueError('Unsupported fixed decision type')
        prompt=self.renderer.render(state,question,system=self.system[lang])
        result=self.read(self.url,prompt,letters,n_probs=self.plan['n_probs'],cache_prompt=self.plan['cache_prompt'],session=self.session)
        missing=bool(result['missing']) or any(k not in result['probs'] for k in letters)
        # Do not interpret omitted top-k candidates as zero probabilities.
        score=None if missing else (result['probs']['A'] if mode=='paired' else sum(result['probs'][k] for k in 'BCD'))
        return {'score':score,'mode':mode,'model_size':self.model_size,'prompt_sha256':__import__('hashlib').sha256(prompt.encode()).hexdigest(),**result}


def score_j(arm, model_size, mode, new_text, lang, old_text=None):
    if arm.model_size!=model_size:raise ValueError('Loaded J model size mismatch')
    return arm.score_j(new_text,lang,mode,old_text)
