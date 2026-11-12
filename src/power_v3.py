"""Power estimate for the v0.3 E4B-vs-26B comparison (protocol-v0.3 §12 item 6).

Decision rule (jevlike v3, copied into protocol-v0.3 §6): "明顯掉" = gap >= 5 points AND exact
McNemar p < 0.05. Discordance priors come from jevlike results/ladder.json D0 (the six H2 tasks:
E4B-wrong/26B-right 6-17%, reverse 0-4%) and from a noisier symmetric-ish case. Twin pairs are
treated as independent items (a mild optimistic bias; reported as a limitation).
Also reports the expected 95% half-width of the paired accuracy difference, which bounds what
"相當"（H14: GLiNER vs 26B) can claim. No model inference; pure simulation, fixed seed.
"""
import json
import math
import random
from pathlib import Path

SEED = 20261112
REPS = 4000
# (name, P(E4B wrong & 26B right), P(E4B right & 26B wrong)) -> true gap = b - c
SCENARIOS = [
    ('gap5_one_sided', 0.06, 0.01),
    ('gap5_noisy', 0.09, 0.04),
    ('gap8_jevlike_median', 0.10, 0.02),
    ('gap10_jevlike_strong', 0.12, 0.02),
    ('gap0_null', 0.04, 0.04),
]
TEST_N_PER_TYPE = {'60_per_type': 40, '90_per_type': 60, '120_per_type': 80}  # 2/3 of items go to test
N_TYPES = 10


def mcnemar_exact_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def simulate(n, pb, pc, rng):
    hits, gaps = 0, []
    for _ in range(REPS):
        b = c = 0
        for _ in range(n):
            u = rng.random()
            if u < pb:
                b += 1
            elif u < pb + pc:
                c += 1
        gap = (b - c) / n
        gaps.append(gap)
        hits += gap >= 0.05 and mcnemar_exact_p(b, c) < 0.05
    gaps.sort()
    return {'power': hits / REPS, 'gap_p2.5': gaps[int(REPS * 0.025)], 'gap_p97.5': gaps[int(REPS * 0.975)]}


def main(out=Path('results/power-v3')):
    rng = random.Random(SEED)
    rows = []
    for size, n_type in TEST_N_PER_TYPE.items():
        for level, n in (('per_type', n_type), ('overall', n_type * N_TYPES)):
            for name, pb, pc in SCENARIOS:
                r = simulate(n, pb, pc, rng)
                rows.append({'size': size, 'level': level, 'n_test': n, 'scenario': name,
                             'p_e4b_wrong_26b_right': pb, 'p_e4b_right_26b_wrong': pc, **r})
                print(f"{size:13s} {level:8s} n={n:4d} {name:22s} power={r['power']:.2f} "
                      f"gap95=[{r['gap_p2.5']:+.3f},{r['gap_p97.5']:+.3f}]", flush=True)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'power.json').write_text(json.dumps({'seed': SEED, 'reps': REPS, 'rule': 'gap>=0.05 and exact McNemar p<0.05',
                                                'rows': rows}, indent=2) + '\n')


if __name__ == '__main__':
    main()
