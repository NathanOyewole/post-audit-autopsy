# Post-Audit Autopsy

**Can AI models reason about smart-contract exploits they haven't memorized?**

An eval that measures whether models can find real vulnerabilities in smart contracts — and, critically, whether they can do it on **novel variants** of bugs they may have seen before.

Built for the micro1 Eval Hackathon.

**Video walkthrough:** [link to be added — YouTube/Loom/Drive]

---

## 1. Domain and expertise

Smart-contract security. The author hunts vulnerabilities in deployed EVM contracts (see `scout`, a Rust contract-hunt engine with an Immunefi bounty radar) and reviews AI-generated code daily. This eval comes from a real workflow gap: AI coding agents are increasingly asked to audit contracts, and we have no good measure of whether they can do it on anything they haven't memorized.

## 2. What the eval tests and why the gap matters

Frontier models are trained on public post-mortems (The DAO, Euler, Nomad). Score them on those and you're measuring **memorization, not reasoning**. Worse, small models happily invent vulnerabilities in safe code.

The eval isolates the difference with three sets:

| Set | What | Purpose |
|---|---|---|
| **A** | 5 compact real/relevant vulnerable contracts | models may have memorized these |
| **B** | 5 size-matched **mutations** of Set A (renamed/restructured, same bug) | no memorized answer |
| **C** | 2 large real contracts (The DAO, SpankChain) | complexity control |
| **controls** | 2 benign contracts | false-positive rate |

**The A vs B gap is the headline.** A large gap means models rely on pattern recall, not reasoning.

Each task gives the model a contract source and asks:

> Identify the critical vulnerability. Explain root cause, impact, and fix.

## 3. Key finding

Free models can find simple, self-contained bugs (access control, overflow) but **struggle with realistic complexity**: large codebases, cross-function reentrancy, and avoiding false positives on benign code. Model scale helps, but even the largest free model fails on the hardest real-world cases.

Full results: `RESULTS.md`.

## 4. Scoring rubric (0–10 per task)

| Dimension | Max |
|---|---|
| Root cause match | 4 |
| Impact / severity | 2 |
| Exploit path | 2 |
| Fix proposal | 2 |

Grading uses an LLM judge (`reflection/beam-1.0-501b-a23b:free`) with the reference post-mortem. The judge prompt is in `harness/config.py` (`JUDGE_PROMPT`). The judge runs at temperature 0 and its JSON is parsed strictly; malformed responses are retried up to 4 times.

## 5. Models, settings, and scores

**Models** (free, on Nous Portal):

- `upstage/solar-mini4:free`
- `meituan/longcat-2.5:free`
- `reflection/beam-1.0-501b-a23b:free`

**Settings:** temperature 0, 1 run per task, max_tokens 8192, judge temperature 0.

**Run date:** 2026-11-06 / 2026-11-07.

| model | Set A | Set B | A−B | Set C | controls |
|---|---|---|---|---|---|
| meituan/longcat-2.5:free | 5.40 | 7.00 | −1.60 | 5.00 | 6.50 |
| reflection/beam-1.0-501b-a23b:free | 9.40 | 8.80 | +0.60 | 5.00 | 7.00 |
| upstage/solar-mini4:free | 4.60 | 2.00 | +2.60 | 0.50 | 0.00 |
| **mean** | **6.47** | **5.93** | **+0.53** | **3.50** | **4.50** |

## 6. Failure analysis

1. **Model scale dominates.** The largest model (reflection/beam) scores highest on every set.
2. **Large contracts are the biggest drop.** Set C averages **3.5/10** vs Set A **6.47/10** — complexity is a major bottleneck.
3. **Small models hallucinate.** solar-mini4 scored **0/10 on both benign controls** — it invented bugs in safe code.
4. **The memorization gap is real but model-dependent.** solar-mini4 shows the predicted A>B gap (+2.6); reflection is flat (+0.6); longcat is reversed (−1.6).
5. **Hard cases all models miss.** SpankChain (real 2018 reentrancy, ~800 lines) was failed by all three.

Per-task scores and raw outputs are in `results/`.

## 7. Setup and run (clean environment)

Requires Python 3.10+ and an OpenAI-compatible API key (Nous Portal, OpenRouter, Oxion AI, or any compatible endpoint).

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials (any OpenAI-compatible endpoint)
cp .env.example .env   # then edit .env
# or export directly:
# export OPENAI_BASE_URL=https://inference-api.nousresearch.com/v1
# export OPENAI_API_KEY=your-key-here

# 3. Build the task set
python harness/build_tasks.py

# 4. Run the models (resumes automatically, backs off on rate limits)
python harness/runner.py

# 5. Grade against references
python harness/grader.py

# 6. Summarize
python harness/report.py
```

**Runtime:** 42 model calls at ~30–120s each, plus judge calls; expect 1–3 hours with free-tier rate limits. The runner resumes automatically if interrupted.

**Cost:** $0 with free models.

## 8. Layout

```
tasks/
  set_a/        compact real/relevant vulnerable contracts
  set_b/        mutated variants (same bugs, renamed)
  set_c/        large real contracts (complexity control)
  controls/     benign contracts
harness/
  config.py     models, rubric, prompts, temperature
  build_tasks.py
  mutate.py     identifier-renaming mutation generator
  runner.py     model runner (rate-limit aware)
  grader.py     LLM judge
  report.py     summary + A/B gap
  package.py    build the submission ZIP
results/
  raw.jsonl     raw model outputs
  graded.jsonl  scores per output
  summary.json  per-model, per-set means
external/
  not-so-smart-contracts/   source of the real-world examples
```

## 9. Prior work and sources

- `crytic/not-so-smart-contracts` — real-world vulnerable contract examples (Trail of Bits). Used for the Set A sources.
- Post-mortems: The DAO (Phil Daian, 2016), King of the Ether, SpankChain (2018), Rubixi.
- Mutation method: identifier renaming via `harness/mutate.py`, preserving semantics.

## 10. Limitations

- Free models only (frontier models were not available on the free plan). Results are therefore a lower bound on frontier capability.
- The LLM judge is itself a free model; its scores are a proxy for expert grading.
- The task set is small (12 + 2 controls); it is designed for signal, not statistical power.
