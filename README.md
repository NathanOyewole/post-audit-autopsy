# Post-Audit Autopsy

**Can frontier AI models reason about smart-contract exploits they haven't memorized?**

An eval that measures whether models can find real vulnerabilities in smart contracts, and — critically — whether they can do it on **novel variants** of bugs they may have seen before.

## The question

Frontier models have likely seen famous post-mortems (The DAO, Parity, Euler) in training. So scoring well on those proves little. The real test is a **structurally identical bug they've never seen**.

## Design

Two parallel sets of 5 contracts:

- **Set A — real, famous exploits** (The DAO, Rubixi, King of the Ether, SpankChain, Unprotected). Models may have memorized the answers.
- **Set B — mutated variants** of the same bug classes (renamed, restructured, different constants). Same semantics, no memorized answer.
- **Controls — 2 benign contracts** to measure false-positive rate.

**The gap between Set A and Set B is the finding.** A large gap means models rely on pattern recall, not reasoning.

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

## Models

Free models available on Nous Portal:

- `upstage/solar-mini4:free`
- `stepfun/step-3.7-flash:free`
- `meituan/longcat-2.5:free`
- `reflection/beam-1.0-501b-a23b:free`

## Reproduce

```bash
# 1. Build the task set
python harness/build_tasks.py

# 2. Run the models (resumes automatically, backs off on rate limits)
python harness/runner.py

# 3. Grade against references
python harness/grader.py

# 4. Summarize
python harness/report.py
```

## Layout

```
tasks/
  set_a/        real, famous exploits (with public source)
  set_b/        mutated variants (same bug classes)
  controls/     benign contracts
harness/
  config.py     models, rubric, prompts
  build_tasks.py
  runner.py     model runner (rate-limit aware)
  grader.py     LLM judge
  report.py     summary + A/B gap
results/
  raw.jsonl     model answers
  graded.jsonl  scored answers
  summary.json  per-model, per-set means
external/
  not-so-smart-contracts/   source of the real-world examples
```

## Sources

- `crytic/not-so-smart-contracts` — real-world vulnerable contract examples
- Post-mortems: The DAO (Phil Daian), Parity multisig, King of the Ether, SpankChain, Rubixi
