#!/usr/bin/env python3
"""
start_factory.py — Maneki-AI Smart Factory Orchestrator (Phase 4)

Launches both the API Gateway and the Task Listener concurrently.
Handles graceful shutdown on Ctrl+C.
"""

import os
import sys
import signal
import subprocess
import time

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
API_GATEWAY_SCRIPT = os.path.join(PROJECT_ROOT, "core", "api_gateway.py")
TASK_LISTENER_SCRIPT = os.path.join(PROJECT_ROOT, "core", "task_listener.py")


def print_banner():
    """Print the startup banner."""
    print("=" * 50)
    print("  === Maneki-AI Smart Factory Running ===")
    print("  -> API Gateway active on http://localhost:8000")
    print("  -> Task Listener actively polling queue...")
    print("=" * 50)
    print("  Press Ctrl+C to stop all services.\n")


def start_factory():
    """Launch API Gateway and Task Listener as subprocesses."""
    processes = []

    try:
        # Start API Gateway
        gateway_proc = subprocess.Popen(
            [sys.executable, API_GATEWAY_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT,
            text=True,
            bufsize=1
        )
        processes.append(("API Gateway", gateway_proc))

        # Small delay to let gateway start cleanly
        time.sleep(0.5)

        # Start Task Listener
        listener_proc = subprocess.Popen(
            [sys.executable, TASK_LISTENER_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=PROJECT_ROOT,
            text=True,
            bufsize=1
        )
        processes.append(("Task Listener", listener_proc))

        print_banner()

        # Continuously read and forward output from both processes
        while True:
            for name, proc in processes:
                # Check if process is still alive
                if proc.poll() is not None:
                    print(f"[start_factory] ERROR: {name} exited unexpectedly (code {proc.returncode}).")
                    raise SystemExit(1)

            # Read a line from each process (non-blocking via timeout)
            for name, proc in processes:
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line:
                        print(line.rstrip())

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n[start_factory] Shutdown signal received. Stopping all services...")
    except SystemExit:
        print("\n[start_factory] A service failed. Shutting down all services...")
    finally:
        cleanup(processes)


def cleanup(processes):
    """Gracefully terminate all subprocesses."""
    for name, proc in processes:
        if proc.poll() is None:
            print(f"[start_factory] Stopping {name} (PID {proc.pid})...")
            if sys.platform == "win32":
                # On Windows, use taskkill to terminate the process tree
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                os.kill(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            print(f"[start_factory] {name} stopped.")

    print("[start_factory] Maneki-AI Smart Factory shut down complete.")


if __name__ == "__main__":
    start_factory()
