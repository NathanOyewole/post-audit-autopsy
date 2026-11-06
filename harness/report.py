"""Summarize graded results: per-model, per-set, and the A/B gap."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def load_graded():
    p = RESULTS / "graded.jsonl"
    if not p.exists():
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def main():
    rows = load_graded()
    if not rows:
        print("no graded results yet")
        return

    models = sorted({r["model"] for r in rows})
    sets = ["set_a", "set_b", "controls"]

    print(f"{'model':40s} {'A':>6s} {'B':>6s} {'gap':>6s} {'ctrl':>6s} {'n':>4s}")
    print("-" * 72)
    summary = {}
    for m in models:
        line = {s: [] for s in sets}
        for r in rows:
            if r["model"] != m or not r.get("grade", {}).get("ok"):
                continue
            line[r["set"]].append(r["grade"]["total"])
        a = sum(line["set_a"]) / len(line["set_a"]) if line["set_a"] else 0
        b = sum(line["set_b"]) / len(line["set_b"]) if line["set_b"] else 0
        c = sum(line["controls"]) / len(line["controls"]) if line["controls"] else 0
        n = sum(len(v) for v in line.values())
        print(f"{m:40s} {a:6.2f} {b:6.2f} {a-b:6.2f} {c:6.2f} {n:4d}")
        summary[m] = {
            "set_a_mean": round(a, 2),
            "set_b_mean": round(b, 2),
            "gap": round(a - b, 2),
            "control_mean": round(c, 2),
            "n": n,
            "per_task": {r["task_id"]: r["grade"]["total"] for r in rows if r["model"] == m and r.get("grade", {}).get("ok")},
        }

    with open(RESULTS / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nwrote results/summary.json")


if __name__ == "__main__":
    main()
