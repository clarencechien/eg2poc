"""Render results/synthetic-v3/summary.json into report.md (tables only; conclusions live in summary.md)."""
import json
from pathlib import Path

OUT = Path('results/synthetic-v3')
NAMES = {'C_encode_one_text': 'C（每段編碼一次）', 'J_e2b': 'J-E2B', 'J_e4b': 'J-E4B', 'J_26b': 'J-26B', 'GD1': 'GD1', 'DM_gliner': 'DM-GLiNER', 'DM_eg2': 'DM-EG2',
         'D2_NLI': 'D2 NLI', 'Rule': '規則', 'C': 'C'}
VERDICT = {'clearly higher': '明顯較高', 'clearly lower': '明顯較低', 'comparable': '相當',
           'significant but below the 5-point threshold': '顯著，但未達 5 點門檻',
           'not distinguishable (underpowered)': '分不出（檢定力不足）', 'n/a': '—'}


def pct(v):
    return '—' if v is None else f'{100 * v:.1f}'


def cell(a):
    if not a:
        return '—'
    s = f"{pct(a['acc'])} [{pct(a['ci95'][0])}, {pct(a['ci95'][1])}]"
    if a.get('coverage', 1) < 0.999:
        s += f" ·覆蓋 {100 * a['coverage']:.0f}%"
    return s


def gap(d):
    if not d:
        return '—'
    return (f"{100 * d['gap']:+.1f} 點 [{100 * d['ci95'][0]:+.1f}, {100 * d['ci95'][1]:+.1f}]，p = {d['mcnemar_p']:.2g}，"
            f"n = {d['n']}（{d['a_only']} / {d['b_only']}）")


def main():
    s = json.loads((OUT / 'summary.json').read_text())
    arms = s['arms']
    L = ['# v0.3 評分結果（表格）', '',
         f"由 `src/report_v3.py` 產生、`src/render_v3.py` 排版。測試集 {s['n_test']} 段原題，校準集 {s['n_cal']} 段。"
         '準確率單位為 %，括號內是依 pair_id 叢集 bootstrap 的 95% CI（1,000 次）。'
         '覆蓋率未滿 100% 的 arm，準確率只算有答案的題目（缺值不填零）。', '',
         '## 1. 單段四選一準確率（測試集）', '',
         '| 範圍 | ' + ' | '.join(NAMES[a] for a in arms) + ' |', '|---|' + '---|' * len(arms)]
    for k in ('overall', 'G1', 'G2', 'G3', 'lang:zh', 'lang:en'):
        label = {'overall': '**整體**', 'lang:zh': 'zh', 'lang:en': 'en'}.get(k, k)
        L.append(f'| {label} | ' + ' | '.join(cell(s['accuracy'][k][a]) for a in arms) + ' |')
    L += ['', '### 1.1 各題型（只描述，不做判讀）', '', '| 題型 | ' + ' | '.join(NAMES[a] for a in arms) + ' |', '|---|' + '---|' * len(arms)]
    for k in ('H-noi', 'H-dis', 'H-inv', 'H-inc', 'H-bor', 'H-imp', 'H-res', 'H-tmp', 'H-dat', 'H-lng'):
        L.append(f'| {k} | ' + ' | '.join(pct((s['accuracy'][k][a] or {}).get('acc')) for a in arms) + ' |')
    L += ['', '### 1.2 敏感度：排除盲判者自行標記為歧義的題目', '', '| 範圍 | ' + ' | '.join(NAMES[a] for a in arms) + ' |', '|---|' + '---|' * len(arms)]
    for k, v in s['accuracy_unflagged'].items():
        L.append(f'| {k} | ' + ' | '.join(pct((v[a] or {}).get('acc')) for a in arms) + ' |')
    h = s['hypotheses']
    L += ['', '## 2. 假說判讀（protocol §6，判讀規則預先寫死）', '']
    if 'H12' in h:
        L += ['**H12：J-26B 對 J-E4B**', '', '| 範圍 | 差距 [95% CI]，McNemar | 判讀 |', '|---|---|---|']
        for k, d in h['H12'].items():
            L.append(f'| {k} | {gap(d)} | {VERDICT[d["verdict"]]} |')
    if 'H13' in h:
        L += ['', f"**H13：J-E2B ≥ 95% 的題型**：{', '.join(h['H13']['easy_types']) or '無'}"]
    if 'H14' in h:
        d = h['H14']
        L += ['', f"**H14：J-26B 對 DM-GLiNER（G1+G2）**：{gap(d)}。差距 CI 上限 {100 * d['ci95'][1]:.1f} 點，"
              f"門檻 < 5 點 → {'成立' if d['pass'] else '不成立'}"]
    if h.get('H15'):
        d = h['H15']
        L += ['', f"**H15：H-dat「先算好」減原始，J-26B**：{gap(d)} → {'成立（≥ 8 點）' if d['pass'] else '不成立（< 8 點）'}", '',
              '| arm | 先算好 − 原始 | 只有先算好版答對／只有原始版答對 | n | p |', '|---|---|---|---|---|']
        for a, v in h['H15_all_arms'].items():
            if v:
                L.append(f"| {NAMES[a]} | {100 * v['gap']:+.1f} 點 | {v['a_only']} / {v['b_only']} | {v['n']} | {v['mcnemar_p']:.2g} |")
    if 'H16' in h:
        d = h['H16']
        L += ['', f"**H16：GD1 對 J-26B**：{gap(d)}，判讀「{VERDICT[d['verdict']]}」；GD1 改寫一致率 "
              f"{pct(d['gd1_consistency'])}% → {'成立' if d['pass'] else '不成立'}"]
    L += ['', '## 3. 一致性與孿生題', '', '| arm | 改寫＋選項順序一致率（Q6） | n | 孿生題兩題都對 | n |', '|---|---|---|---|---|']
    for a in arms:
        c, t = s['q6_consistency'][a], s['twin_both_correct'][a]
        L.append(f"| {NAMES[a]} | {pct(c['consistency'])} | {c['n']} | {pct(t['rate'])} | {t['n']} |")
    L += ['', '## 4. 校準（溫度在校準集擬合，測試集報告）', '', '| arm | 溫度 | ECE 原始 → 校準後 | Brier 原始 → 校準後 | 錯誤偵測 AUROC |', '|---|---|---|---|---|']
    for a, c in s['calibration'].items():
        f = lambda v: '—' if v is None else f'{v:.3f}'  # noqa: E731
        L.append(f"| {NAMES[a]} | {f(c['temperature'])} | {f(c['ece_raw'])} → {f(c['ece_cal'])} | {f(c['brier_raw'])} → {f(c['brier_cal'])} | {f(c['error_detection_auroc'])} |")
    L += ['', '## 5. 變更偵測（P，測試集）', '',
          '「推導」= 兩段各自判斷再比較（1 − Σ P_old·P_new）；「直接」= 一次給兩版問有沒有變。門檻在校準集決定。'
          '校準集的負例只有約 70 組，少於 100 組時「1% 誤報」的門檻就是負例最高分，因此與「0% 誤報」相同。', '',
          '| arm:做法 | AUROC | 0% 誤報門檻：召回／實際誤報 | 1% 誤報門檻：召回／實際誤報 | 校準門檻準確率 | 覆蓋 |', '|---|---|---|---|---|---|']
    for n, v in s['P'].items():
        a, way = n.split(':')
        f0, f1 = v.get('fpr0', {}), v.get('fpr1', {})
        L.append(f"| {NAMES[a]}:{'推導' if way == 'derived' else '直接'} | {pct(v['auroc_test'])} | {pct(f0.get('test_recall'))} / {pct(f0.get('test_fpr'))} | "
                 f"{pct(f1.get('test_recall'))} / {pct(f1.get('test_fpr'))} | {pct(v.get('acc_test_at_cal_threshold'))} | {100 * v['coverage']:.0f}% |")
    if 'H17' in h:
        L += ['', '**H17：推導 ≥ 直接？**', '', '| arm | 推導 AUROC | 直接 AUROC | 成立 |', '|---|---|---|---|']
        for a, v in h['H17'].items():
            L.append(f"| {NAMES[a]} | {pct(v['derived_auroc'])} | {pct(v['direct_auroc'])} | {'是' if v.get('pass') else '否'} |")
    if 'H18' in h:
        ok = [n for n, v in h['H18'].items() if v['pass']]
        bad = [n for n, v in h['H18'].items() if not v['pass']]
        L += ['', f"**H18：校準集 1% 誤報門檻在測試集的實際誤報 ≤ 2%**：通過 {len(ok)} 項；未通過：{', '.join(bad) or '無'}"]
    L += ['', '## 6. 成本（同機比較）', '', '| arm | 平均 | p50 | p95 | 機器 |', '|---|---|---|---|---|']
    machine = {'J_e2b': 'Modal L4', 'J_e4b': 'Modal L4', 'J_26b': 'Modal L4', 'GD1': 'Google 雲端（含網路，8 併發）'}
    for a, c in s['cost'].items():
        name = NAMES.get(a, a)
        ms = lambda k: f"{c[k]:.0f} ms" if c.get(k) is not None else '—'  # noqa: E731
        L.append(f"| {name} | {ms('mean_ms')} | {ms('p50_ms')} | {ms('p95_ms')} | {machine.get(a, '本容器 CPU 4 核')} |")
    L.append('')
    (OUT / 'report.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L[:20]))


if __name__ == '__main__':
    main()
