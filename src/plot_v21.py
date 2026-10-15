"""Standalone scientific figure for complete J results and measured CPU cost."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_comparison(report, baseline, output):
    if not all(report['models'][s]['status'] == 'complete' for s in ('e2b', 'e4b')):
        return False
    contrasts = ('T5-word', 'T6-word', 'T7-word', 'T8-sentence', 'T8-paragraph')
    arms = ('C_alt_classification', 'D2_alt_single', 'J_e2b_single', 'J_e4b_single')
    values = [[baseline['primary'][c][arm]['auc'] for c in contrasts] for arm in arms[:2]]
    for size in ('e2b', 'e4b'):
        values.append([report['models'][size]['metrics'][c][f'J_{size}_single']['auc'] for c in contrasts])
    matrix = np.array([[np.nan if v is None else v for v in row] for row in values])
    labels = ('C-alt distribution drift', 'D2-alt single', 'J E2B single', 'J E4B single')
    fig, (quality, cost) = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw={'width_ratios': [1.7, 1]}, layout='constrained')
    quality.imshow(np.ma.masked_invalid(matrix), cmap='YlGnBu', vmin=0, vmax=1, aspect='auto')
    quality.set_yticks(range(4), labels=labels)
    quality.set_xticks(range(5), labels=('T5\ndate', 'T6\nword', 'T7\nword', 'T8\nsentence', 'T8\nparagraph'))
    quality.set_title('AUROC with matched-base controls')
    for y, row in enumerate(matrix):
        for x, value in enumerate(row):
            quality.text(x, y, 'missing' if np.isnan(value) else f'{value:.3f}', ha='center', va='center', color='white' if value > .6 else 'black')
    names = ('C_alt_classification', 'D2_alt_single', 'J_e2b', 'J_e4b')
    means = [report['costs'][name]['latency_ms']['mean'] for name in names]
    p95 = [report['costs'][name]['latency_ms']['p95'] for name in names]
    cost.barh(range(4), means, color='#307898', label='Mean')
    cost.scatter(p95, range(4), marker='|', s=130, color='#d05a30', label='p95', zorder=3)
    cost.invert_yaxis()
    cost.set_yticks(range(4), labels=('C-alt', 'D2-alt', 'J E2B', 'J E4B'))
    cost.set_xscale('log')
    cost.set_xlim(min(means) / 2, max(p95) * 2.7)
    for y, value in enumerate(means):
        cost.text(max(value, p95[y]) * 1.12, y, f'{value:,.0f}', va='center', fontsize=9)
    cost.set_xlabel('Milliseconds per input (log scale)')
    cost.set_title('Same CPU, same 100 inputs')
    cost.legend(loc='lower right', fontsize=8)
    fig.suptitle('Rule-generated corpus only; 4 CPU threads; J Q8_0', fontsize=12)
    folder = output / 'fig'
    folder.mkdir(exist_ok=True)
    for extension in ('png', 'svg'):
        fig.savefig(folder / f'j-quality-cost.{extension}', dpi=180)
    plt.close(fig)
    return True
