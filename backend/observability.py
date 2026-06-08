"""Observability — log every request to a JSONL file.

The JD lists 'production observability'. This is the minimal version: one JSON
line per query with what was retrieved, what was recommended, confidence, and
latency — so you can audit and debug the system after the fact.
"""
import json
from datetime import datetime, timezone

import config


def log_event(event: dict) -> None:
    config.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    with open(config.LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
