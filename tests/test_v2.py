import json
import unittest
from collections import Counter
from pathlib import Path
from src.gen_synthetic_v2 import generate, FORMS, lexicon_hits
from src.common import read_jsonl, digest
from src.arms import score_r, score_d2, score_docset

class V2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path('data/synthetic-v2')
        cls.config=json.loads((cls.root/'config.json').read_text())
        cls.bases,cls.pairs,cls.docs=generate(cls.config)
    def test_reproduction_and_hashes(self):
        manifest=json.loads((self.root/'manifest.json').read_text())
        for f,h in manifest['sha256'].items():self.assertEqual(digest(self.root/f),h)
        for name,rows in [('base',self.bases),('pairs',self.pairs),('docsets',self.docs)]:self.assertEqual(read_jsonl(self.root/f'{name}.jsonl'),rows)
    def test_distinct_bases_and_skeletons(self):
        for lang in ('zh','en'):
            for form,_,_ in FORMS[lang]:
                self.assertEqual(len({p['base_id'] for p in self.pairs if p['category']=='T6' and p['strength']=='word' and p['lang']==lang and p['subcategory']==form}),30)
        self.assertTrue(all(n>=20 for n in Counter((b['lang'],b['skeleton']) for b in self.bases).values()))
    def test_label_disjointness(self):
        for lang in ('zh','en'):
            self.assertEqual(lexicon_hits(' '.join(self.config['labels_alt'][lang]),self.config['v2']['perturbation_lexicon'][lang],lang),[])
        self.assertEqual(lexicon_hits('Work has been cancelled.', ['cancel'], 'en'),['cancel'])
    def test_matched_dates(self):
        mapping={p['pair_id']:p for p in self.pairs}
        for p in self.pairs:
            for cid in p['control_ids']:self.assertEqual(mapping[cid]['base_id'],p['base_id'])
            if p['category'] in ('T4','T5'):
                self.assertEqual(score_r(p['old_text'],p['new_text'],p['lang'],self.config['date_regex']),p['label'])
                self.assertEqual(sum(a!=b for a,b in zip(p['old_text'],p['new_text'])),1)
    def test_dates_missing_invalid_and_ambiguous(self):
        regex=self.config['date_regex'];t='Planned delivery: 2026-11-15. Deadline: 2026-11-20.'
        self.assertIsNone(score_r(t,'date missing','en',regex))
        self.assertIsNone(score_r(t,t.replace('11-15','11-99'),'en',regex))
        self.assertIsNone(score_r(t,t+' Planned delivery: 2026-11-16.','en',regex))
    def test_d2_and_docset_missing(self):
        p=[[.8,.1,.1],[.1,.2,.7],[.1,.3,.6],[.1,.2,.7]]
        q=[p[1],p[0],p[2],p[3]]
        result=score_d2(p,q,0,2)
        self.assertEqual(result['argmax'],1);self.assertEqual(result['single'],.8)
        zero=[[.3,.4,.3]]*4
        self.assertIsNone(score_d2(zero,zero,0,2)['paired'])
        self.assertIsNone(score_docset([.1,None,.2],.3)['max'])
        self.assertEqual(score_docset([.1,.2,.3],.3)['trigger'],0)
    def test_docsets_matched_and_distinct(self):
        mapping={p['pair_id']:p for p in self.pairs}
        self.assertEqual(len(self.docs),80)
        self.assertTrue(all(n==2 for n in Counter(d['matched_set_id'] for d in self.docs).values()))
        for d in self.docs:
            self.assertEqual(len({mapping[pid]['skeleton'] for pid in d['pair_ids']}),3)
            self.assertFalse(d['independently_verified'])
            self.assertTrue(all(mapping[pid]['label']==d['label'] for pid in d['pair_ids']))

if __name__=='__main__':unittest.main()
