# Maneki-AI Web Frontend Architecture

## Overview

The Maneki-AI web frontend is a **Streamlit** single-page application deployed on **Render** at `https://maneki-ai.onrender.com/`. It provides a task management console that interfaces with the internal Maneki-AI Smart Factory pipeline.

---

## Directory Structure

```
Maneki-AI/
├── app.py                  # Render deployment entry point
├── render.yaml             # Render service configuration
├── requirements.txt        # Python dependencies (incl. streamlit)
├── runtime.txt             # Python 3.12.0
├── web/
│   ├── __init__.py         # Package marker
│   ├── api.py              # API client & data schema layer
│   └── ui.py               # Streamlit UI components
├── task_queue/
│   ├── pending/            # Tasks awaiting processing
│   ├── processing/         # Tasks currently being executed
│   └── completed/          # Finished tasks
├── logs/                   # Execution logs & reports
│   ├── task_[id].log       # Full stdout/stderr log
│   └── task_[id]_report.json  # Structured status report
├── core/
│   ├── api_gateway.py      # HTTP API (POST /api/task, GET /api/health)
│   └── task_listener.py    # Background task processor
└── scripts/                # Executable worker scripts
```

---

## Data Schema: Task

The lightweight file-based task schema is defined in `web/api.py`:

| Field        | Type   | Description                                      |
|-------------|--------|--------------------------------------------------|
| `task_id`    | str    | Unique identifier (e.g. `TASK_20260602_001`)     |
| `status`     | str    | `PENDING` / `PROCESSING` / `SUCCESS` / `FAILED`  |
| `parameters` | dict   | Payload with `script_name` and optional extras   |
| `result_log` | str    | Path to `logs/task_[task_id]_report.json`        |
| `created_at` | str    | ISO-8601 timestamp of creation                   |
| `updated_at` | str    | ISO-8601 timestamp of last update                |

Tasks are stored as JSON files in `task_queue/` directories. The `core/task_listener.py` moves files through the pipeline: `pending → processing → completed`.

---

## API Contract

### Internal API Gateway (`core/api_gateway.py`)

| Method | Endpoint         | Description                          |
|--------|------------------|--------------------------------------|
| POST   | `/api/task`      | Inject a new task into pending queue |
| GET    | `/api/health`    | Health check                         |

### Web Frontend API Client (`web/api.py`)

| Function            | Description                                      |
|---------------------|--------------------------------------------------|
| `submit_task()`     | Writes task JSON to `pending/` + POSTs to Gateway|
| `get_task_status()` | Scans queues & logs for a task's current status  |
| `list_all_tasks()`  | Aggregates all tasks across all queues & logs    |
| `read_task_report()`| Reads `logs/task_[id]_report.json`               |
| `read_task_log()`   | Reads `logs/task_[id].log`                       |

---

## UI Pages (`web/ui.py`)

### 1. 📋 Submit Task
- Form with auto-generated `task_id`, `script_name`, and optional JSON parameters
- "Submit Task" button → calls `submit_task()` → writes to `task_queue/pending/` → status = `PENDING`
- Shows recent 5 submissions below the form

### 2. 📊 Task Dashboard
- Summary metrics: total / pending / processing / completed
- Filterable task list by status
- Each task expandable to show parameters, timestamps, and a "View Report" button

### 3. 📄 Execution Report
- Dropdown selector for completed tasks
- Structured report display (status, task_id, timestamp, full JSON)
- Full execution log viewer with download button
- File path references for debugging

---

## Task Submission Flow

```
User clicks "Submit Task"
        │
        ▼
web/ui.py → submit_task(task_id, script_name, params)
        │
        ├──► Writes JSON to task_queue/pending/task_[id].json  (status: PENDING)
        │
        └──► POST /api/task to API Gateway (best-effort)
                │
                ▼
        core/task_listener.py picks up the file
                │
                ├──► Moves to task_queue/processing/  (status: PROCESSING)
                ├──► Executes script via subprocess
                ├──► Writes logs/task_[id].log
                ├──► Writes logs/task_[id]_report.json  (status: SUCCESS/FAILED)
                └──► Moves to task_queue/completed/
```

---

## Render Deployment

- **Service**: `maneki-ai` (Python web service)
- **Entry Point**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- **Build**: `pip install -r requirements.txt`
- **Runtime**: Python 3.12.0 (via `runtime.txt`)
- **Config**: `render.yaml` defines env vars and start command

The `app.py` file simply imports and runs `web.ui.main()`, keeping the deployment entry point clean and the UI logic modular.

---

## Cross-Platform Compatibility

- All file paths use `os.path.join()` for Windows/Linux/macOS compatibility
- No platform-specific dependencies
- Streamlit runs identically on all platforms
- File-based task queue avoids database dependency (no SQLite/PostgreSQL needed)
