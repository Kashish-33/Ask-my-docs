import json
import os
from datetime import datetime

LOG_PATH = "./data/logs.jsonl"


def log_attempt(session_id: str, attempt_number: int, query: str, score: int, reason: str):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "attempt": attempt_number,
        "query": query,
        "score": score,
        "reason": reason
    }

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")