#!/usr/bin/env python3
"""
task_listener.py — Maneki-AI MVP Task Listener (Phase 4)

Continuously polls 'task_queue/pending/' for .json task files.
When a task is discovered, it:
  - Moves the file to task_queue/processing/
  - Parses the JSON for task_id, script_name, and success_criteria
  - Executes the script via subprocess
  - Captures stdout/stderr
  - Writes a detailed log to logs/task_[task_id].log
  - Generates a structured status report to logs/task_[task_id]_report.json
  - Sends an outbound callback to N8N_CALLBACK_URL (if configured)
  - Moves the original task file to task_queue/completed/
"""

import os
import sys
import time
import json
import glob
import shutil
import subprocess
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# Paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "pending")
PROCESSING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "processing")
COMPLETED_DIR = os.path.join(PROJECT_ROOT, "task_queue", "completed")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
POLL_INTERVAL = 5  # seconds

# Outbound callback URL — read from environment variable with fallback
N8N_CALLBACK_URL = os.environ.get("N8N_CALLBACK_URL", "")


def ensure_directories():
    """Ensure all required directories exist."""
    for d in [PENDING_DIR, PROCESSING_DIR, COMPLETED_DIR, LOGS_DIR]:
        os.makedirs(d, exist_ok=True)


def timestamp():
    """Return an ISO-8601 formatted timestamp string."""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def discover_tasks():
    """Scan the pending directory for .json files and return their paths."""
    if not os.path.isdir(PENDING_DIR):
        print(f"[task_listener] WARNING: Pending directory not found at {PENDING_DIR}")
        return []
    json_files = glob.glob(os.path.join(PENDING_DIR, "*.json"))
    return json_files


def move_file(src, dst_dir):
    """Move a file from src to dst_dir, preserving the filename."""
    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.move(src, dst)
    return dst


def parse_task(task_path):
    """Parse a JSON task file and return the data dict, or None on error."""
    try:
        with open(task_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"[task_listener] ERROR: Failed to parse task file {task_path}: {e}")
        return None


def execute_script(script_name):
    """
    Execute a script using subprocess.
    Returns (returncode, stdout, stderr).
    The script path is resolved relative to PROJECT_ROOT.
    """
    script_path = os.path.join(PROJECT_ROOT, script_name)
    if not os.path.isfile(script_path):
        return (-1, "", f"Script not found: {script_path}")

    print(f"[task_listener] Executing: {script_path}")
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=PROJECT_ROOT
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return (-1, "", "ERROR: Script execution timed out (120s)")
    except Exception as e:
        return (-1, "", f"ERROR: Script execution failed: {e}")


def write_task_log(task_id, stdout, stderr, returncode):
    """Write a detailed execution log to logs/task_[task_id].log."""
    log_path = os.path.join(LOGS_DIR, f"task_{task_id}.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"Task ID: {task_id}\n")
        f.write(f"Execution Timestamp: {timestamp()}\n")
        f.write(f"Exit Code: {returncode}\n")
        f.write(f"{'='*60}\n")
        f.write("STDOUT:\n")
        f.write(f"{'='*60}\n")
        f.write(stdout if stdout else "(no stdout)\n")
        f.write(f"\n{'='*60}\n")
        f.write("STDERR:\n")
        f.write(f"{'='*60}\n")
        f.write(stderr if stderr else "(no stderr)\n")
    print(f"[task_listener] Log written: {log_path}")
    return log_path


def write_status_report(task_id, returncode, parameters=None):
    """
    Generate a structured status report JSON file.
    Outputs the full Task Schema: task_id, status, parameters,
    result_log, created_at, updated_at.
    """
    status = "SUCCESS" if returncode == 0 else "FAILED"
    now = timestamp()
    report = {
        "task_id": task_id,
        "status": status,
        "parameters": parameters or {},
        "result_log": os.path.join(LOGS_DIR, f"task_{task_id}_report.json"),
        "created_at": now,
        "updated_at": now,
    }
    report_path = os.path.join(LOGS_DIR, f"task_{task_id}_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[task_listener] Status report written: {report_path}")
    return report_path



def send_callback(task_id):
    """
    Send an outbound HTTP POST callback to N8N_CALLBACK_URL (if configured).
    Reads the status report from logs/task_[task_id]_report.json and posts it.
    Wraps the network call in a try-except so failures don't crash the listener.
    """
    if not N8N_CALLBACK_URL:
        print(f"[task_listener] Callback skipped: N8N_CALLBACK_URL not configured.")
        return

    report_path = os.path.join(LOGS_DIR, f"task_{task_id}_report.json")
    if not os.path.isfile(report_path):
        print(f"[task_listener] Callback skipped: Report file not found at {report_path}")
        return

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        data = json.dumps(payload).encode("utf-8")
        req = Request(
            N8N_CALLBACK_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        resp = urlopen(req, timeout=10)
        print(f"[task_listener] Callback sent to {N8N_CALLBACK_URL} — HTTP {resp.status}")
        resp.close()

    except URLError as e:
        print(f"[task_listener] Callback failed: n8n unreachable ({e.reason})")
    except Exception as e:
        print(f"[task_listener] Callback skipped or failed: {e}")


def process_task(task_path):
    """Process a single task file through its full lifecycle."""
    task_name = os.path.basename(task_path)
    print(f"\n[task_listener] Discovered new task: {task_name}")

    # Step a: Move from pending -> processing
    processing_path = move_file(task_path, PROCESSING_DIR)
    print(f"[task_listener] Moved to: {processing_path}")

    # Step b: Parse the JSON
    task_data = parse_task(processing_path)
    if task_data is None:
        # If parsing fails, move to completed with a failure report
        task_id = task_name.replace(".json", "")
        write_task_log(task_id, "", f"Failed to parse task file: {task_name}", -1)
        write_status_report(task_id, 1)
        send_callback(task_id)
        move_file(processing_path, COMPLETED_DIR)
        return

    task_id = task_data.get("task_id", task_name.replace(".json", ""))
    parameters = task_data.get("parameters", {})
    script_name = parameters.get("script_name", "")
    success_criteria = task_data.get("success_criteria", "")

    print(f"[task_listener] task_id: {task_id}")
    print(f"[task_listener] script_name: {script_name}")
    print(f"[task_listener] success_criteria: {success_criteria}")

    # Step c & d: Execute script and capture output
    returncode, stdout, stderr = execute_script(script_name)

    # Step e: Write execution log
    write_task_log(task_id, stdout, stderr, returncode)

    # Step f: Write status report
    write_status_report(task_id, returncode)

    # Step f2: Send outbound callback (if configured)
    send_callback(task_id)

    # Step g: Move from processing -> completed
    move_file(processing_path, COMPLETED_DIR)
    print(f"[task_listener] Task {task_id} completed. Status: {'SUCCESS' if returncode == 0 else 'FAILED'}")


def main():
    print(f"[task_listener] Maneki-AI Task Listener (Phase 4) started.")
    print(f"[task_listener] Watching: {PENDING_DIR}")
    print(f"[task_listener] Poll interval: {POLL_INTERVAL}s")
    if N8N_CALLBACK_URL:
        print(f"[task_listener] Outbound callback URL: {N8N_CALLBACK_URL}")
    else:
        print(f"[task_listener] Outbound callback: DISABLED (set N8N_CALLBACK_URL to enable)")

    ensure_directories()
    known_tasks = set()

    try:
        while True:
            tasks = discover_tasks()

            for task_path in tasks:
                task_name = os.path.basename(task_path)
                if task_name not in known_tasks:
                    known_tasks.add(task_name)
                    process_task(task_path)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("\n[task_listener] Shutting down gracefully.")


if __name__ == "__main__":
    main()
