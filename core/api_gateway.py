#!/usr/bin/env python3
"""
api_gateway.py — Maneki-AI HTTP API Gateway (Phase 3)

A lightweight HTTP server using Python's built-in libraries.
Provides endpoints for n8n and Agent-S to push tasks into the factory.

Endpoints:
  POST /api/task  — Inject a new task into the pending queue
  GET  /api/health — Health check endpoint

Default port: 8000
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PENDING_DIR = os.path.join(PROJECT_ROOT, "task_queue", "pending")

DEFAULT_PORT = 8000


def ensure_pending_dir():
    """Ensure the pending directory exists."""
    os.makedirs(PENDING_DIR, exist_ok=True)


def validate_task_payload(payload):
    """
    Validate that the incoming JSON payload contains the required fields.
    Returns (is_valid, error_message).
    """
    if not isinstance(payload, dict):
        return False, "Payload must be a JSON object."

    task_id = payload.get("task_id")
    if not task_id or not isinstance(task_id, str) or not task_id.strip():
        return False, "Missing or invalid 'task_id'. Must be a non-empty string."

    parameters = payload.get("parameters")
    if not isinstance(parameters, dict):
        return False, "Missing or invalid 'parameters'. Must be a JSON object."

    script_name = parameters.get("script_name")
    if not script_name or not isinstance(script_name, str) or not script_name.strip():
        return False, "Missing or invalid 'parameters -> script_name'. Must be a non-empty string."

    return True, ""


def save_task_to_pending(payload):
    """
    Save the validated payload as a JSON file in the pending queue.
    Returns the filename that was created.
    """
    task_id = payload["task_id"]
    filename = f"task_{task_id}.json"
    filepath = os.path.join(PENDING_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return filename


class ManekiAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Maneki-AI API Gateway."""

    def _send_json_response(self, status_code, data):
        """Send a JSON response with the given status code and data dict."""
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        """Read and parse the JSON body from the request. Returns None on error."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return None
        raw = self.rfile.read(content_length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/task":
            self._handle_post_task()
        else:
            self._send_json_response(404, {
                "error": "Not Found",
                "message": f"Endpoint POST {parsed_path.path} not found."
            })

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        if parsed_path.path == "/api/health":
            self._handle_get_health()
        else:
            self._send_json_response(404, {
                "error": "Not Found",
                "message": f"Endpoint GET {parsed_path.path} not found."
            })

    def _handle_post_task(self):
        """Process a POST /api/task request."""
        payload = self._read_json_body()

        if payload is None:
            self._send_json_response(400, {
                "error": "Bad Request",
                "message": "Invalid or empty JSON body. Please send a valid JSON payload."
            })
            return

        # Validate the payload
        is_valid, error_msg = validate_task_payload(payload)
        if not is_valid:
            self._send_json_response(400, {
                "error": "Bad Request",
                "message": error_msg
            })
            return

        # Save to pending queue
        ensure_pending_dir()
        try:
            filename = save_task_to_pending(payload)
        except IOError as e:
            self._send_json_response(500, {
                "error": "Internal Server Error",
                "message": f"Failed to save task file: {str(e)}"
            })
            return

        # Return success
        task_id = payload["task_id"]
        self._send_json_response(201, {
            "status": "QUEUED",
            "task_id": task_id,
            "message": "Task injected into pending queue successfully."
        })
        print(f"[api_gateway] Task {task_id} queued -> {filename}")

    def _handle_get_health(self):
        """Process a GET /api/health request."""
        self._send_json_response(200, {
            "status": "HEALTHY",
            "engine": "Maneki-AI"
        })

    def log_message(self, format, *args):
        """Override default logging to add a prefix."""
        sys.stderr.write(f"[api_gateway] {args[0]} {args[1]} {args[2]}\n")


def run_server(host="0.0.0.0", port=DEFAULT_PORT):
    """Start the HTTP API Gateway server."""
    server = HTTPServer((host, port), ManekiAPIHandler)
    print(f"[api_gateway] Maneki-AI API Gateway starting...")
    print(f"[api_gateway] Listening on http://{host}:{port}")
    print(f"[api_gateway] Endpoints:")
    print(f"[api_gateway]   POST /api/task   — Inject a new task")
    print(f"[api_gateway]   GET  /api/health  — Health check")
    print(f"[api_gateway] Pending queue: {PENDING_DIR}")
    print(f"[api_gateway] Press Ctrl+C to stop.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[api_gateway] Shutting down gracefully.")
        server.server_close()


if __name__ == "__main__":
    # Allow port override via command-line argument
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"[api_gateway] Invalid port '{sys.argv[1]}'. Using default port {DEFAULT_PORT}.")

    run_server(port=port)
