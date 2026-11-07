"""Run models against eval tasks via the Nous OpenAI-compatible API.

Handles free-tier rate limits with backoff and resumes from existing results.
"""
import json, os, sys, time, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
RESULTS_DIR = ROOT / "results"


def load_tasks():
    tasks = []
    for set_name in ["set_a", "set_b", "set_c", "controls"]:
        d = TASKS_DIR / set_name
        if not d.exists():
            continue
        for f in sorted(d.glob("*.json")):
            t = json.load(open(f))
            t["set"] = t.get("set", set_name)
            t["source_file"] = str(f)
            tasks.append(t)
    return tasks


def make_client():
    creds = config.nous_credentials()
    return OpenAI(base_url=creds["base_url"], api_key=creds["api_key"], max_retries=0)


def run_one(client, model, task, timeout=600):
    prompt = config.TASK_PROMPT.format(source=task["source"])
    delay = 20
    for attempt in range(6):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=8192,
                temperature=config.TEMPERATURE,
                timeout=timeout,
            )
            msg = resp.choices[0].message
            content = msg.content or ""
            if not content.strip():
                # some models spend the whole budget on reasoning; recover it
                content = getattr(msg, "reasoning_content", None) or ""
            return {"ok": True, "answer": content, "finish": resp.choices[0].finish_reason}
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                print(f"    429 rate limit, sleeping {delay}s (attempt {attempt+1})", flush=True)
                time.sleep(delay)
                delay = min(delay * 2, 180)
                continue
            return {"ok": False, "error": msg}
    return {"ok": False, "error": "rate limited after retries"}


def completed_pairs():
    done = set()
    p = RESULTS_DIR / "raw.jsonl"
    if p.exists():
        for line in open(p):
            if not line.strip():
                continue
            r = json.loads(line)
            if r.get("ok"):
                done.add((r["model"], r["task_id"]))
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=config.MODELS)
    ap.add_argument("--sets", nargs="*", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=4.0)
    args = ap.parse_args()

    tasks = load_tasks()
    if args.sets:
        tasks = [t for t in tasks if t["set"] in args.sets]
    if args.limit:
        tasks = tasks[: args.limit]

    done = completed_pairs()
    client = make_client()
    RESULTS_DIR.mkdir(exist_ok=True)
    out = []
    for model in args.models:
        for task in tasks:
            if (model, task["id"]) in done:
                print(f"[{model}] {task['id']} ... (skip, done)", flush=True)
                continue
            print(f"[{model}] {task['id']} ...", flush=True)
            res = run_one(client, model, task)
            row = {
                "model": model,
                "task_id": task["id"],
                "set": task["set"],
                "ok": res["ok"],
                "answer": res.get("answer"),
                "error": res.get("error"),
                "ts": int(time.time()),
            }
            out.append(row)
            with open(RESULTS_DIR / "raw.jsonl", "a") as f:
                f.write(json.dumps(row) + "\n")
            time.sleep(args.sleep)
    print(json.dumps({"runs": len(out), "ok": sum(1 for r in out if r["ok"])}))


if __name__ == "__main__":
    main()
