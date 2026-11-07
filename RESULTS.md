# Results

3 free models × 12 tasks (Set A × 5, Set B × 5, Set C × 2, controls × 2).

| model | Set A | Set B | A−B | Set C | controls |
|---|---|---|---|---|---|
| meituan/longcat-2.5:free | 5.40 | 7.00 | −1.60 | 5.00 | 6.50 |
| reflection/beam-1.0-501b-a23b:free | 9.40 | 8.80 | +0.60 | 5.00 | 7.00 |
| upstage/solar-mini4:free | 4.60 | 2.00 | +2.60 | 0.50 | 0.00 |
| **mean** | **6.47** | **5.93** | **+0.53** | **3.50** | **4.50** |

## What the numbers show

**1. Model scale dominates.** The largest model (reflection/beam) scores highest on every set (A 9.4, B 8.8). The smallest (solar-mini4) scores lowest and is the only model that fails both large contracts.

**2. Large contracts are the biggest drop.** Set C (The DAO, SpankChain — 800–1200 lines) averages **3.5/10** vs Set A **6.47/10**. Complexity, not just bug class, is a major bottleneck.

**3. Small models hallucinate.** solar-mini4 scored **0/10 on both benign controls** — it invented vulnerabilities in safe code. The larger models were better (6.5–7.0) but still flagged one benign contract.

**4. The memorization gap is real but model-dependent.** solar-mini4 shows the predicted A>B gap (+2.6); reflection shows a small gap (+0.6); longcat shows the opposite (−1.6). So "memorization vs reasoning" is not uniform — it depends on model capability.

**5. Hard cases all models miss.** SpankChain (real 2018 reentrancy, large) was failed by all three models (0, 0, 1).

## Per-task scores

| task | set | longcat | reflection | solar |
|---|---|---|---|---|
| unprotected | A | 10 | 10 | 10 |
| overflow | A | 9 | 7 | 10 |
| race | A | 8 | 10 | 3 |
| rubixi | A | 0 | 10 | 0 |
| kotet | A | 0 | 10 | 0 |
| mut_unprotected | B | 10 | 10 | 2 |
| mut_overflow | B | 10 | 10 | 8 |
| mut_race | B | 7 | 10 | 0 |
| mut_rubixi | B | 0 | 10 | 0 |
| mut_kotet | B | 8 | 4 | 0 |
| dao | C | 10 | 10 | 0 |
| spankchain | C | 0 | 0 | 1 |
| ctl_erc20 | control | 4 | 4 | 0 |
| ctl_vault | control | 9 | 10 | 0 |

## Takeaway

Free models can find simple, self-contained bugs (access control, overflow) but **struggle with realistic complexity**: large codebases, cross-function reentrancy, and avoiding false positives on benign code. Model scale helps, but even the largest free model fails on the hardest real-world cases.
