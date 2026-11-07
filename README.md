# Post-Audit Autopsy

**Can AI models reason about smart-contract exploits they haven't memorized?**

An eval that measures whether models can find real vulnerabilities in smart contracts — and, critically, whether they can do it on **novel variants** of bugs they may have seen before.

Built for the micro1 Eval Hackathon.

## Why this matters

Frontier models are trained on public post-mortems (The DAO, Euler, Nomad). Score them on those and you're measuring **memorization, not reasoning**. Worse, small models happily invent vulnerabilities in safe code — a false-positive rate that makes them unusable for real security work.

This eval isolates the difference.

## Design

| Set | What | Purpose |
|---|---|---|
| **A** | 5 compact real/relevant vulnerable contracts | models may have memorized these |
| **B** | 5 size-matched **mutations** of Set A (renamed/restructured, same bug) | no memorized answer |
| **C** | 2 large real contracts (The DAO, SpankChain) | complexity control |
| **controls** | 2 benign contracts | false-positive rate |

**The A vs B gap is the headline.** A large gap means models rely on pattern recall, not reasoning. Set C isolates the effect of code size/complexity. Controls measure how often models cry wolf.

## Tasks

Each task gives the model a contract source and asks:

> Identify the critical vulnerability. Explain root cause, impact, and fix.

## Grading rubric (0–10 per task)

| Dimension | Max |
|---|---|
| Root cause match | 4 |
| Impact / severity | 2 |
| Exploit path | 2 |
| Fix proposal | 2 |

Grading uses an LLM judge with the reference post-mortem, strict on root cause.

## Results (3 free models × 12 tasks)

| model | Set A | Set B | A−B | Set C | controls |
|---|---|---|---|---|---|
| meituan/longcat-2.5:free | 5.40 | 7.00 | −1.60 | 5.00 | 6.50 |
| reflection/beam-1.0-501b-a23b:free | 9.40 | 8.80 | +0.60 | 5.00 | 7.00 |
| upstage/solar-mini4:free | 4.60 | 2.00 | +2.60 | 0.50 | 0.00 |
| **mean** | **6.47** | **5.93** | **+0.53** | **3.50** | **4.50** |

### Findings

1. **Model scale dominates.** The largest model (reflection/beam) scores highest on every set.
2. **Large contracts are the biggest drop.** Set C averages **3.5/10** vs Set A **6.47/10** — complexity is a major bottleneck.
3. **Small models hallucinate.** solar-mini4 scored **0/10 on both benign controls** — it invented bugs in safe code.
4. **The memorization gap is real but model-dependent.** solar-mini4 shows the predicted A>B gap (+2.6); reflection is flat (+0.6); longcat is reversed (−1.6).
5. **Hard cases all models miss.** SpankChain (real 2018 reentrancy, ~800 lines) was failed by all three.

Full per-task table: see `RESULTS.md`.

## Models

Free models on Nous Portal (no cost):

- `upstage/solar-mini4:free`
- `meituan/longcat-2.5:free`
- `reflection/beam-1.0-501b-a23b:free`

(`stepfun/step-3.7-flash:free` is in the catalog but was rate-limited throughout the run.)

## Reproduce

Requirements: Python 3.10+, an OpenAI-compatible endpoint (Nous Portal), and the `openai` package.

```bash
pip install openai

# 1. Build the task set (needs external/not-so-smart-contracts cloned)
python harness/build_tasks.py

# 2. Run the models (resumes automatically, backs off on rate limits)
python harness/runner.py

# 3. Grade against references
python harness/grader.py

# 4. Summarize
python harness/report.py
```

Notes:
- `harness/config.py` holds the model list and API config; credentials are read from `~/.hermes/auth.json`.
- The runner recovers answers from `reasoning_content` when a model spends its whole token budget on reasoning.
- Approximate runtime: 42 model calls at ~30–120s each, plus judge calls; expect 1–3 hours with free-tier rate limits.
- Cost: $0 (free models).

## Layout

```
tasks/
  set_a/        compact real/relevant vulnerable contracts
  set_b/        mutated variants (same bugs, renamed)
  set_c/        large real contracts (complexity control)
  controls/     benign contracts
harness/
  config.py     models, rubric, prompts
  build_tasks.py
  mutate.py     identifier-renaming mutation generator
  runner.py     model runner (rate-limit aware)
  grader.py     LLM judge
  report.py     summary + A/B gap
  package.py    build the submission ZIP
results/
  raw.jsonl     model answers
  graded.jsonl  scored answers
  summary.json  per-model, per-set means
external/
  not-so-smart-contracts/   source of the real-world examples
```

## Sources

- `crytic/not-so-smart-contracts` — real-world vulnerable contract examples
- Post-mortems: The DAO (Phil Daian), King of the Ether, SpankChain, Rubixi
