"""Eval configuration: models, API, rubric."""
import json, os

# Nous Portal credentials (read from Hermes auth)
AUTH_PATH = os.path.expanduser("~/.hermes/auth.json")


def nous_credentials():
    d = json.load(open(AUTH_PATH))
    p = d["providers"]["nous"]
    return {
        "base_url": p["inference_base_url"].rstrip("/"),
        "api_key": p.get("agent_key") or p.get("access_token"),
    }


# Free models accessible on this Nous plan
MODELS = [
    "upstage/solar-mini4:free",
    "stepfun/step-3.7-flash:free",
    "meituan/longcat-2.5:free",
    "reflection/beam-1.0-501b-a23b:free",
]

# Grading rubric (0-10 per task)
RUBRIC = {
    "root_cause": 4,      # identifies the actual vulnerability mechanism
    "impact": 2,          # funds at risk / severity
    "exploit_path": 2,    # concrete attack path / steps
    "fix": 2,             # correct fix
}

TASK_PROMPT = """You are a smart-contract security auditor.

Below is the source code of a smart contract deployed on an EVM chain. It was later exploited, resulting in a loss of funds.

Identify the critical vulnerability. Be precise and concrete.

Respond in this exact format:
ROOT CAUSE: <the vulnerability mechanism, 2-4 sentences>
IMPACT: <what an attacker can steal or break, and the severity>
EXPLOIT PATH: <concrete step-by-step attack>
FIX: <the specific code change that prevents it>

Do not speculate about bugs that are not there. If you are unsure, say so.

CONTRACT:
{source}
"""

JUDGE_PROMPT = """You are grading a security audit answer against a reference.

REFERENCE ROOT CAUSE: {ref_root_cause}
REFERENCE IMPACT: {ref_impact}
REFERENCE EXPLOIT PATH: {ref_exploit}
REFERENCE FIX: {ref_fix}

CANDIDATE ANSWER:
{answer}

Score each dimension 0-{max_root} (root cause), 0-{max_impact} (impact), 0-{max_exploit} (exploit path), 0-{max_fix} (fix).
Be strict: only award root-cause points if the candidate identifies the actual mechanism, not a vague or wrong one.

Respond as JSON only:
{{"root_cause": <int>, "impact": <int>, "exploit_path": <int>, "fix": <int>, "reasoning": "<one sentence>"}}
"""
