"""Summarize graded results: per-model, per-set, and the A/B gap.

Set A = real/famous exploits (may be memorized)
Set B = mutated variants (novel, same bug classes)
Set C = large contracts (complexity control)
Controls = benign (high score = correctly rejected as non-vulnerable)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def load_graded():
    p = RESULTS / "graded.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    rows = load_graded()
    if not rows:
        print("no graded results yet")
        return

    models = sorted({r["model"] for r in rows})
    sets = ["set_a", "set_b", "set_c", "controls"]

    print(f"{'model':38s} {'A':>6s} {'B':>6s} {'A-B':>6s} {'C':>6s} {'ctrl':>6s} {'n':>4s}")
    print("-" * 74)
    summary = {}
    for m in models:
        line = {s: [] for s in sets}
        for r in rows:
            if r["model"] != m or not r.get("grade", {}).get("ok"):
                continue
            line[r["set"]].append(r["grade"]["total"])
        a, b = mean(line["set_a"]), mean(line["set_b"])
        c, ctrl = mean(line["set_c"]), mean(line["controls"])
        n = sum(len(v) for v in line.values())
        print(f"{m:38s} {a:6.2f} {b:6.2f} {a-b:6.2f} {c:6.2f} {ctrl:6.2f} {n:4d}")
        summary[m] = {
            "set_a_mean": round(a, 2),
            "set_b_mean": round(b, 2),
            "gap_A_minus_B": round(a - b, 2),
            "set_c_mean": round(c, 2),
            "control_accuracy": round(ctrl, 2),
            "n": n,
            "per_task": {r["task_id"]: r["grade"]["total"] for r in rows if r["model"] == m and r.get("grade", {}).get("ok")},
        }

    with open(RESULTS / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nwrote results/summary.json")


if __name__ == "__main__":
    main()
