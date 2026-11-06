"""Grade raw answers against reference solutions using an LLM judge."""
import json, sys, time, argparse, re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "results"
TASKS_DIR = ROOT / "tasks"


def load_tasks():
    tasks = {}
    for set_name in ["set_a", "set_b", "controls"]:
        d = TASKS_DIR / set_name
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            t = json.load(open(f))
            tasks[t["id"]] = t
    return tasks


def make_client():
    creds = config.nous_credentials()
    return OpenAI(base_url=creds["base_url"], api_key=creds["api_key"])


def grade_one(client, judge_model, task, answer):
    ref = task["reference"]
    prompt = config.JUDGE_PROMPT.format(
        ref_root_cause=ref.get("root_cause", ""),
        ref_impact=ref.get("impact", ""),
        ref_exploit=ref.get("exploit", ""),
        ref_fix=ref.get("fix", ""),
        answer=answer,
        max_root=config.RUBRIC["root_cause"],
        max_impact=config.RUBRIC["impact"],
        max_exploit=config.RUBRIC["exploit_path"],
        max_fix=config.RUBRIC["fix"],
    )
    try:
        resp = client.chat.completions.create(
            model=judge_model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            timeout=180,
        )
        text = resp.choices[0].message.content or ""
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return {"ok": False, "error": "no json", "raw": text[:300]}
        data = json.loads(m.group(0))
        total = sum(int(data.get(k, 0)) for k in ["root_cause", "impact", "exploit_path", "fix"])
        return {"ok": True, **data, "total": total}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="reflection/beam-1.0-501b-a23b:free")
    ap.add_argument("--raw", default=str(RESULTS_DIR / "raw.jsonl"))
    args = ap.parse_args()

    tasks = load_tasks()
    client = make_client()
    rows = [json.loads(l) for l in open(args.raw) if l.strip()]
    out = []
    for r in rows:
        if not r.get("ok") or not r.get("answer"):
            out.append({**r, "grade": {"ok": False, "error": r.get("error")}})
            continue
        task = tasks.get(r["task_id"])
        if not task:
            out.append({**r, "grade": {"ok": False, "error": "task not found"}})
            continue
        g = grade_one(client, args.judge, task, r["answer"])
        out.append({**r, "grade": g})
        print(f"[{r['model']}] {r['task_id']} -> {g.get('total', 'ERR')}", flush=True)
        time.sleep(1)

    with open(RESULTS_DIR / "graded.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")

    # summary
    by_model = {}
    for r in out:
        if r["grade"].get("ok"):
            by_model.setdefault(r["model"], []).append(r["grade"]["total"])
    summary = {m: {"n": len(v), "mean": round(sum(v) / len(v), 2), "scores": v} for m, v in by_model.items()}
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
