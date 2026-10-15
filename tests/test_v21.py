import json
import unittest
from pathlib import Path
from src.common import digest,read_jsonl
from src.j_arm import JArm,score_j
from src.report_v2 import matched

class Recorder:
    def render(self,state,question,system):
        self.state,self.question,self.system=state,question,system
        return 'rendered by upstream'

class V21Tests(unittest.TestCase):
    def setUp(self):
        self.plan=json.loads(Path('data/synthetic-v2.1/analysis-plan.json').read_text())
        self.config=json.loads(Path('data/synthetic-v2/config.json').read_text())
    def arm(self,result):
        arm=JArm.__new__(JArm);arm.plan=self.plan;arm.config=self.config
        arm.renderer=Recorder();arm.system={'zh':'system','en':'system'};arm.model_size='e2b';arm.url='http://127.0.0.1';arm.session=None
        arm.read=lambda *args,**kwargs:result
        return arm
    def test_fixed_plan_and_100_shared_bench_rows(self):
        manifest=json.loads(Path('data/synthetic-v2.1/manifest.json').read_text())
        for f,h in manifest['sha256'].items():self.assertEqual(digest(Path('data/synthetic-v2.1')/f),h)
        self.assertEqual(len(set(self.plan['benchmark_pair_ids'])),100)
        ids={p['pair_id'] for p in read_jsonl('data/synthetic-v2/pairs.jsonl')}
        self.assertTrue(set(self.plan['benchmark_pair_ids'])<=ids)
    def test_single_never_receives_old(self):
        arm=self.arm({'missing':[],'probs':{'A':.1,'B':.2,'C':.3,'D':.4}})
        result=arm.score_j('new paragraph','en','single','secret old paragraph')
        self.assertAlmostEqual(result['score'],.9)
        self.assertEqual(arm.renderer.state,'new paragraph')
        self.assertEqual(list(arm.renderer.question['options'].values()),self.config['labels_alt']['en'])
    def test_top_k_missing_is_not_zero(self):
        arm=self.arm({'missing':['D'],'probs':{'A':.7,'B':.2,'C':.1}})
        self.assertIsNone(arm.score_j('new','zh')['score'])
        arm=self.arm({'missing':[],'probs':{'A':.7,'B':.2,'C':.1}})
        self.assertIsNone(arm.score_j('new','en')['score'])
    def test_paired_existing_boolean_and_size_guard(self):
        arm=self.arm({'missing':[],'probs':{'A':.8,'B':.2}})
        self.assertEqual(arm.score_j('new','en','paired','old')['score'],.8)
        self.assertIn('old',arm.renderer.state);self.assertIn('new',arm.renderer.state)
        with self.assertRaises(ValueError):score_j(arm,'e4b','single','new','en')
    def test_matched_controls_do_not_use_other_bases(self):
        rows=[{'pair_id':'positive','category':'T5','strength':'word','control_ids':['negative']},
              {'pair_id':'negative','category':'T4','strength':'word'},
              {'pair_id':'unrelated','category':'T4','strength':'word'}]
        scores={'positive':{'A':.2},'negative':{'A':.3},'unrelated':{'A':0}}
        self.assertEqual(matched(rows,scores,'T5-word','A')['auc'],0)
        scores['negative']['A']=None
        self.assertIsNone(matched(rows,scores,'T5-word','A')['auc'])

    def test_combo_evaluation_is_limited_to_registered_contrasts(self):
        result=matched([],{},'T6-sentence','final_same')
        self.assertIsNone(result['auc'])
        self.assertIn('not applicable',result['status'])

if __name__=='__main__':unittest.main()
