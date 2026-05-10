from __future__ import annotations

from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime
from threading import Lock
from typing import Any, Dict, Optional


_CURRENT_RUN_ID: ContextVar[Optional[str]] = ContextVar("current_run_id", default=None)
_RUNS: Dict[str, Dict[str, Any]] = {}
_LOCK = Lock()


def now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def create_run(run_id: str) -> None:
    with _LOCK:
        _RUNS[run_id] = {
            "run_id": run_id,
            "status": "queued",
            "current_node": "queued",
            "events": [],
            "result": None,
            "error": None,
            "created_at": now_text(),
            "updated_at": now_text(),
        }


def set_current_run(run_id: Optional[str]) -> None:
    _CURRENT_RUN_ID.set(run_id)


def add_event(
    node: str,
    message: str,
    event_type: str = "info",
    data: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
) -> None:
    target_run_id = run_id or _CURRENT_RUN_ID.get()
    if not target_run_id:
        return
    with _LOCK:
        run = _RUNS.get(target_run_id)
        if not run:
            return
        run["status"] = "running" if run["status"] == "queued" else run["status"]
        run["current_node"] = node
        run["updated_at"] = now_text()
        run["events"].append(
            {
                "time": run["updated_at"],
                "node": node,
                "type": event_type,
                "message": message,
                "data": data or {},
            }
        )


def set_result(run_id: str, result: Dict[str, Any]) -> None:
    with _LOCK:
        run = _RUNS[run_id]
        run["status"] = "completed"
        run["current_node"] = "completed"
        run["result"] = result
        run["updated_at"] = now_text()


def set_error(run_id: str, error: str) -> None:
    with _LOCK:
        run = _RUNS[run_id]
        run["status"] = "failed"
        run["current_node"] = "failed"
        run["error"] = error
        run["updated_at"] = now_text()


def get_run(run_id: str) -> Optional[Dict[str, Any]]:
    with _LOCK:
        run = _RUNS.get(run_id)
        return deepcopy(run) if run else None
