# Post-Audit Autopsy — Video Script (5 min)

## 0:00–0:30 — Hook
- "Frontier AI models can find reentrancy in a 20-line contract. But can they find a bug they've never seen before?"
- Title: **Post-Audit Autopsy**

## 0:30–1:30 — The problem
- Models are trained on public post-mortems (The DAO, Euler, Nomad). Score them on those and you're measuring memorization, not reasoning.
- Real question: **can they reason about novel variants?**

## 1:30–2:30 — Design
- 3 sets: **Set A** (compact real/relevant vulnerable contracts), **Set B** (size-matched mutations of the same bugs, renamed), **Set C** (large contracts, complexity control)
- 2 benign controls (false-positive rate)
- Prompt: find the critical vulnerability, explain root cause, impact, exploit, fix
- Rubric 0–10: root cause (4), impact (2), exploit (2), fix (2)
- Graded by an LLM judge against the reference post-mortem

## 2:30–3:30 — Models + harness
- Free models on Nous Portal: solar-mini4, longcat-2.5, reflection/beam
- Runner with rate-limit backoff + auto-resume
- Grader + report pipeline

## 3:30–4:30 — Results
- Show the A vs B table (from results/summary.json)
- The gap = memorization vs reasoning
- Set C = complexity effect
- Controls = false positives

## 4:30–5:00 — Conclusion
- "Models rely on pattern recall. On novel variants of known bugs, performance drops X%."
- Repo: github.com/NathanOyewole/post-audit-autopsy
