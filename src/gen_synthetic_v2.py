"""Frozen v0.2 corpus: deterministic authored templates, never LLM-generated."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from .common import write_jsonl, digest, validate_pairs

SKELETONS = ('weekly', 'adr', 'ticket', 'meeting', 'prd')
TOPICS = {'zh': ['帳務匯出', '權限管理', '訂單追蹤', '庫存同步', '報表查詢', '通知中心'],
          'en': ['billing export', 'access control', 'order tracking', 'inventory sync', 'report search', 'notification center']}
FORMS = {
    'zh': [('沒有', '交付已有資源。', '交付沒有資源。'),
           ('不再', '團隊持續執行。', '團隊不再執行。'),
           ('尚未', '依約應完成的驗收已經完成。', '依約應完成的驗收尚未完成。'),
           ('取消', '執行這項交付。', '取消這項交付。'),
           ('暫停', '繼續這項工作。', '暫停這項工作。')],
    'en': [('no', 'Delivery has resources.', 'Delivery has no resources.'),
           ('no longer', 'Work is still proceeding.', 'Work is no longer proceeding.'),
           ('not yet', 'Acceptance due now is already complete.', 'Acceptance due now is not yet complete.'),
           ('cancel', 'We will execute this delivery.', 'We will cancel this delivery.'),
           ('pause', 'We will continue this work.', 'We will pause this work.')]
}


def skeleton_text(lang, skeleton, project, status, topic, owner='Nora'):
    if lang == 'zh':
        date = '預計交付日為2026-11-15，截止日期為2026-11-20。'
        ahead = '目前進度領先。'
        neutral = '助理整理測試記錄。'
        bodies = {
            'weekly': f'{project}週報：{topic}由{owner}負責。{status}{ahead}{date}{neutral}',
            'adr': f'ADR {project}採用{topic}方案。{date}{neutral}{ahead}決議：{status}負責人為{owner}。',
            'ticket': f'工單{project}：{topic}。{neutral}負責人：{owner}。{status}{date}執行摘要：{ahead}',
            'meeting': f'{project}會議要點：{neutral}{status}由{owner}處理{topic}。{ahead}排程：{date}',
            'prd': f'{project}里程碑／{topic}：{ahead}{date}驗收備註：{neutral}交付安排：{status}窗口：{owner}。',
        }
    else:
        date = 'Planned delivery: 2026-11-15. Deadline: 2026-11-20.'
        ahead = 'Work is ahead of schedule.'
        neutral = 'Assistants record test notes.'
        bodies = {
            'weekly': f'{project} weekly: {owner} owns {topic}. {status} {ahead} {date} {neutral}',
            'adr': f'ADR {project} adopts {topic}. {date} {neutral} {ahead} Decision: {status} Owner: {owner}.',
            'ticket': f'Ticket {project}: {topic}. {neutral} Owner: {owner}. {status} {date} Progress: {ahead}',
            'meeting': f'{project} meeting: {neutral} {status} {owner} handles {topic}. {ahead} Schedule: {date}',
            'prd': f'{project} milestone / {topic}: {ahead} {date} Acceptance note: {neutral} Delivery: {status} Contact: {owner}.',
        }
    return bodies[skeleton]


def lexicon_hits(text, words, lang):
    return [w for w in words if (w in text if lang == 'zh' else
            re.search(r'\b' + re.escape(w) + r'(?:s|ed|led|ing)?\b', text, flags=re.I))]


def generate(config):
    for lang in ('zh', 'en'):
        assert not lexicon_hits(' '.join(config['labels_alt'][lang]), config['v2']['perturbation_lexicon'][lang], lang)
    bases, pairs, docsets = [], [], []
    by_id = {}
    def add(b, category, strength, new, sub=None, control_ids=None, suffix='', label=None):
        pid = f"{b['base_id']}:{category}:{strength}{suffix}"
        if pid in by_id:
            return pid
        row = {'pair_id': pid, 'base_id': b['base_id'], 'lang': b['lang'], 'skeleton': b['skeleton'],
               'category': category, 'subcategory': sub, 'strength': strength, 'generator': 'rule',
               'old_text': b['text'], 'new_text': new, 'label': (None if category == 'T9' else int(category in ('T5','T6','T7','T8'))) if label is None else label,
               'ambiguous': category == 'T9', 'ground_truth_basis': 'authored construction; no independent adjudication',
               'control_ids': control_ids or []}
        pairs.append(row); by_id[pid] = row
        return pid
    def control(b, strength):
        old, lang = b['text'], b['lang']
        if strength == 'word':
            new = old.replace('整理', '彙整') if lang == 'zh' else old.replace('record', 'log')
        elif strength == 'sentence':
            new = old.replace('助理整理測試記錄。', '測試筆記由助理彙整。') if lang == 'zh' else old.replace('Assistants record test notes.', 'Test notes are logged by assistants.')
        else:
            # Rearrange the same facts through a different skeleton; no state change.
            sk = SKELETONS[(SKELETONS.index(b['skeleton']) + 1) % 5]
            new = skeleton_text(lang, sk, b['project'], b['status'], b['topic'])
        return add(b, 'T3', strength, new)
    for lang in ('zh', 'en'):
        for fi, (form, status, flipped) in enumerate(FORMS[lang]):
            for i in range(30):
                sk = SKELETONS[i % 5]; project = f'P{fi}{i:02d}'; topic = TOPICS[lang][i // 5]
                b = {'base_id': f'v2-{lang}-{fi}-{i:02d}', 'project': project, 'lang': lang, 'skeleton': sk,
                     'status': status, 'topic': topic, 'source_kind': 'synthetic_rule', 'generator': 'rule',
                     'text': skeleton_text(lang, sk, project, status, topic)}
                bases.append(b)
                cword = control(b, 'word')
                add(b, 'T6', 'word', b['text'].replace(status, flipped), form, [cword])
                if i < 5:
                    csent = control(b, 'sentence')
                    extended = flipped.rstrip('。.') + ('，這項交付因而無法依原定方案繼續。' if lang == 'zh' else ', so delivery cannot proceed as originally arranged.')
                    add(b, 'T6', 'sentence', b['text'].replace(status, extended), form, [csent])
                if fi < 2 and i < 25:
                    add(b, 'T0', 'word', b['text'])
                if fi != 0:
                    continue
                add(b, 'T1', 'word', b['text'].replace('記錄', '記祿' if i % 2 else '記綠') if lang == 'zh' else b['text'].replace('notes', 'ntoes'))
                add(b, 'T2', 'word', b['text'].replace('。', '。\n', 1) if lang == 'zh' else b['text'].replace('. ', '.\n', 1))
                cdate = add(b, 'T4', 'word', b['text'].replace('2026-11-15', '2026-11-16'))
                add(b, 'T5', 'word', b['text'].replace('2026-11-15', '2026-11-25'), control_ids=[cdate])
                before = '目前進度領先。' if lang == 'zh' else 'Work is ahead of schedule.'
                after = '目前進度落後。' if lang == 'zh' else 'Work is behind schedule.'
                add(b, 'T7', 'word', b['text'].replace(before, after), control_ids=[cword])
                csent = control(b, 'sentence')
                after_sentence = '目前進度落後，無法依約完成交付。' if lang == 'zh' else 'Work is behind schedule and will miss its delivery commitment.'
                add(b, 'T7', 'sentence', b['text'].replace(before, after_sentence), control_ids=[csent])
                t9 = add(b, 'T9', 'sentence', b['text'].replace(status, '').strip())
                blocker = '新增阻礙：外部服務無法使用，交付因此卡關。' if lang == 'zh' else 'New blocker: the external service is unavailable and delivery is blocked.'
                add(b, 'T8', 'sentence', b['text'] + (' ' if lang == 'en' else '') + blocker, control_ids=[csent, t9])
                details = '團隊已向供應商提出處理要求。修復之前無法執行下一步驗收。' if lang == 'zh' else 'The team has asked the vendor for a remedy. The next acceptance step cannot proceed until it is fixed.'
                add(b, 'T8', 'paragraph', b['text'] + '\n' + blocker + (' ' if lang == 'en' else '') + details, control_ids=[control(b, 'paragraph')])
    # T10 is a separate, explicit synthetic risk-policy task, not adjudicated semantics.
    # All three signals together mean a review state; no individual signal suffices.
    for lang in ('zh','en'):
        for i in range(20):
            ids = {0: [], 1: []}
            for j in range(3):
                sk = SKELETONS[(i+j) % 5]; form, status, _ = FORMS[lang][0]
                project = f'D{i:02d}'; topic = TOPICS[lang][i % 6]
                b = {'base_id': f'v2-doc-{lang}-{i:02d}-{j}', 'project': project, 'lang': lang, 'skeleton': sk,
                     'status': status, 'topic': topic, 'source_kind': 'synthetic_rule', 'generator': 'rule',
                     'text': skeleton_text(lang, sk, project, status, topic)}
                bases.append(b)
                positive = [b['text'].replace('2026-11-15','2026-11-16'),
                            b['text'] + ('等客戶確認。' if lang == 'zh' else ' Awaiting client confirmation.'),
                            b['text'].replace('Nora','Mina')][j]
                negative = (b['text'].replace('整理','彙整') if lang == 'zh' else b['text'].replace('record','log'))
                for label, new in ((1,positive),(0,negative)):
                    ids[label].append(add(b,'T10','word',new,suffix=f'-{label}',label=label))
            for label in (0,1):
                docsets.append({'docset_id':f'v2-doc-{lang}-{i:02d}-{label}', 'matched_set_id':f'v2-doc-{lang}-{i:02d}',
                                'lang':lang,'label':label,'pair_ids':ids[label], 'generator':'rule',
                                'ground_truth_basis':'synthetic policy: review state iff date slips AND client confirmation is pending AND owner changes; individually none suffices',
                                'independently_verified':False})
    validate_pairs([p for p in pairs if p['category'] != 'T10'])
    assert len({b['base_id'] for b in bases}) == len(bases)
    for p in pairs:
        for cid in p['control_ids']:
            assert by_id[cid]['base_id'] == p['base_id']
        if p['category'] == 'T5':
            c = by_id[p['control_ids'][0]]
            assert sum(a!=b for a,b in zip(p['old_text'],p['new_text'])) == sum(a!=b for a,b in zip(c['old_text'],c['new_text'])) == 1
    for lang in ('zh','en'):
        for form, _, _ in FORMS[lang]:
            assert len({p['base_id'] for p in pairs if p['lang']==lang and p['category']=='T6' and p['subcategory']==form and p['strength']=='word'}) == 30
    assert sum(p['category']=='T0' for p in pairs)==100
    return bases,pairs,docsets


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='data/synthetic-v2');args=ap.parse_args()
    root=Path(args.output); root.mkdir(parents=True,exist_ok=False)
    config=json.loads(Path('config.json').read_text()); bases,pairs,docsets=generate(config)
    plan={'version':'synthetic-v2','scope':'rule synthetic only; no independent LLM or human adjudication',
          'freeze_before_scoring':True,'seed':config['seed'],'labels_frozen':{k:config[k] for k in ('labels_same','labels_alt','labels_xlang')},
          'primary_controls':'Each positive control_ids explicitly references the same base and strength; T8 sentence has an ambiguous T9 sensitivity, main confirmed-negative table excludes T9.',
          'protocol_interpretation':['Section 3 forbids all label overlap but section 4 explicitly requires C-same overlap; apply the no-overlap constraint to C-alt only.',
             'Word denotes local phrase substitution; equal character counts are enforced only for T5/T4.',
             'T10 constructed three-signal review policy, not independently established semantic status drift; H6 remains exploratory.',
             'D2 paired success cannot establish old text is unnecessary; only D2 single evaluates H4.',
             'H1 relative criterion and absolute <=0.60 lexical criterion can conflict; report both, no causal proof.',
             'Gemini rewrites, independent review, E, B2 and optional D2-DM not run.'],
          'combo':'max(R, D2_single); if R is None use D2_single; only T5, T6-word, T8-sentence',
          'hypotheses':{'H1':'xlang >= same - 0.10 for both T6/T7 word, each prefix', 'H2':'alt between same and xlang',
          'H3':'D2 paired T8 sentence/paragraph >= 0.85','H4':'D2 single T6/T7 word and T8 sentence/paragraph >= 0.80',
          'H5':'R T5/T4 >= 0.95','H6':'exploratory T10 AUROC >=0.80 and positive any-paragraph trigger <0.30',
          'H7':'C across-skeleton AUROC range <0.10; LLM comparison unrun'},
          'noise':'T1 + T3-word; T10 thresholds from T3 only, positive trigger uses any of three paragraphs > p95',
          'limitations':['All slots/templates authored by one generator; no independent samples or real-document accuracy.',
                         'T10 rule is defined in metadata, not given to models; tests generic projection on a stipulated policy.',
                         'AUROC uses matched-base negative pools, not independent sampling; also report within-pair win rate and ties.'],
          'temperature_note':'0.045 inherited, not independently endorsed by official model documentation'}
    for name,rows in [('base',bases),('pairs',pairs),('docsets',docsets)]:write_jsonl(root/f'{name}.jsonl',rows)
    (root/'analysis-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    (root/'config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
    files=['base.jsonl','pairs.jsonl','docsets.jsonl','analysis-plan.json','config.json']
    manifest={'version':'synthetic-v2','sha256':{f:digest(root/f) for f in files},'generator_sha256':digest(__file__),
              'n_bases':len(bases),'n_pairs':len(pairs),'n_docsets':len(docsets),'counts':dict(Counter(p['category'] for p in pairs)),
              'skeleton_language_counts':dict(Counter(f"{b['lang']}/{b['skeleton']}" for b in bases)),
              'generated_with':'deterministic Python rules; zero Gemini calls','independent_validation':False}
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
