"""
web/api.py — Maneki-AI Web Frontend API Client & Data Schema

Provides the lightweight data schema for 'tasks' and the API client
that communicates with the internal API Gateway (core/api_gateway.py).

Task Schema (stored as JSON in task_queue/pending/):
    {
        "task_id":       str   — Unique identifier (e.g. "TASK_20260602_001")
        "status":        str   — "PENDING" | "PROCESSING" | "SUCCESS" | "FAILED"
        "parameters":    dict  — Payload with script_name, etc.
        "result_log":    str   — Path to logs/task_[task_id]_report.json
        "created_at":    str   — ISO-8601 timestamp
        "updated_at":    str   — ISO-8601 timestamp
    }
"""

import os
import json
import glob
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "pending")
PROCESSING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "processing")
COMPLETED_DIR = os.path.join(PROJECT_ROOT, "task_queue", "completed")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

# API Gateway base URL (Render internal or localhost)
API_GATEWAY_URL = os.environ.get(
    "API_GATEWAY_URL",
    "http://localhost:8000"
)


# ── Helpers ────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """Return current UTC time as ISO-8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_dirs():
    """Ensure all required directories exist."""
    for d in [PENDING_DIR, PROCESSING_DIR, COMPLETED_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)


# ── Task Status Lookup ────────────────────────────────────────────────────

def get_task_status(task_id: str) -> dict:
    """
    Look up the current status of a task by scanning queue directories
    and the logs report file.

    Returns a dict with keys: task_id, status, created_at, updated_at,
    result_log (or None if not found).
    """
    # 1. Check if a report file exists
    report_path = os.path.join(LOGS_DIR, f"task_{task_id}_report.json")
    if os.path.isfile(report_path):
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            return {
                "task_id": task_id,
                "status": report.get("status", "UNKNOWN"),
                "result_log": report_path,
                "created_at": report.get("timestamp", ""),
                "updated_at": report.get("timestamp", ""),
                "parameters": report.get("parameters", {}),
            }
        except (json.JSONDecodeError, IOError):
            pass

    # 2. Check pending queue
    pending_path = os.path.join(PENDING_DIR, f"task_{task_id}.json")
    if os.path.isfile(pending_path):
        return {
            "task_id": task_id,
            "status": "PENDING",
            "result_log": None,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "parameters": {},
        }

    # 3. Check processing queue
    processing_path = os.path.join(PROCESSING_DIR, f"task_{task_id}.json")
    if os.path.isfile(processing_path):
        return {
            "task_id": task_id,
            "status": "PROCESSING",
            "result_log": None,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "parameters": {},
        }

    # 4. Check completed queue
    completed_path = os.path.join(COMPLETED_DIR, f"task_{task_id}.json")
    if os.path.isfile(completed_path):
        return {
            "task_id": task_id,
            "status": "COMPLETED",
            "result_log": report_path if os.path.isfile(report_path) else None,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "parameters": {},
        }

    return {
        "task_id": task_id,
        "status": "NOT_FOUND",
        "result_log": None,
        "created_at": "",
        "updated_at": "",
        "parameters": {},
    }


def list_all_tasks() -> list[dict]:
    """
    Aggregate all tasks from all queues and logs into a unified list.
    Each entry follows the Task Schema.
    """
    _ensure_dirs()
    tasks: dict[str, dict] = {}

    # Helper to ingest a JSON file as a task record
    def _ingest(filepath: str, inferred_status: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return
        tid = data.get("task_id", os.path.basename(filepath).replace(".json", ""))
        tasks[tid] = {
            "task_id": tid,
            "status": data.get("status", inferred_status),
            "parameters": data.get("parameters", {}),
            "result_log": data.get("result_log", None),
            "created_at": data.get("created_at", data.get("timestamp", "")),
            "updated_at": data.get("updated_at", data.get("timestamp", "")),
        }

    # Scan pending
    for fp in glob.glob(os.path.join(PENDING_DIR, "*.json")):
        _ingest(fp, "PENDING")

    # Scan processing
    for fp in glob.glob(os.path.join(PROCESSING_DIR, "*.json")):
        _ingest(fp, "PROCESSING")

    # Scan completed
    for fp in glob.glob(os.path.join(COMPLETED_DIR, "*.json")):
        _ingest(fp, "COMPLETED")

    # Scan logs for report files (these have definitive status)
    for fp in glob.glob(os.path.join(LOGS_DIR, "*_report.json")):
        _ingest(fp, "UNKNOWN")

    return list(tasks.values())


# ── Submit Task via API Gateway ───────────────────────────────────────────

def submit_task(task_id: str, script_name: str, extra_params: dict = None) -> dict:
    """
    Submit a new task to the API Gateway (POST /api/task).

    This sets the task status to "PENDING" on the server side and
    prepares the webhook payload for downstream processing.

    Args:
        task_id: Unique identifier for the task.
        script_name: The script to execute (relative to project root).
        extra_params: Optional additional parameters.

    Returns:
        dict with keys: success (bool), task_id, status, message.
    """
    _ensure_dirs()

    payload = {
        "task_id": task_id,
        "parameters": {
            "script_name": script_name,
            **(extra_params or {}),
        },
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }

    # Write directly to pending queue as a fallback
    pending_path = os.path.join(PENDING_DIR, f"task_{task_id}.json")
    try:
        with open(pending_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except IOError as e:
        return {
            "success": False,
            "task_id": task_id,
            "status": "ERROR",
            "message": f"Failed to write task file: {e}",
        }

    # Also attempt to POST to the API Gateway (non-blocking best-effort)
    try:
        data = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{API_GATEWAY_URL}/api/task",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urlopen(req, timeout=5)
    except (URLError, OSError):
        # Gateway may not be running locally; file-based fallback is sufficient
        pass

    return {
        "success": True,
        "task_id": task_id,
        "status": "PENDING",
        "message": f"Task {task_id} submitted. Status set to PENDING.",
    }


# ── Read Execution Report ─────────────────────────────────────────────────

def read_task_report(task_id: str) -> dict | None:
    """
    Read the structured execution report from
    logs/task_[task_id]_report.json.

    Returns the parsed JSON dict, or None if the file does not exist
    or cannot be parsed.
    """
    report_path = os.path.join(LOGS_DIR, f"task_{task_id}_report.json")
    if not os.path.isfile(report_path):
        return None

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def read_task_log(task_id: str) -> str | None:
    """
    Read the full execution log from logs/task_[task_id].log.

    Returns the log content as a string, or None if the file does not exist.
    """
    log_path = os.path.join(LOGS_DIR, f"task_{task_id}.log")
    if not os.path.isfile(log_path):
        return None

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return f.read()
    except IOError:
        return None
