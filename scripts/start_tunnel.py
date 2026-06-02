#!/usr/bin/env python3
"""
start_tunnel.py — Maneki-AI Local Tunnel Provisioner

Provisions a public HTTPS URL for a local port using localtunnel (via npx).
Captures the generated URL and prints it clearly for the user.

Usage:
    python scripts/start_tunnel.py [--port PORT] [--subdomain SUBDOMAIN]

Dependencies:
    - Node.js / npx (localtunnel is fetched on-the-fly, no install needed)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import URLError


def build_npx_command(port: int, subdomain: str | None = None,
                      print_requests: bool = False) -> str:
    """
    Build the npx localtunnel command string.
    Uses shell=True on Windows to handle .cmd files properly.
    """
    cmd = f"npx --yes localtunnel --port {port}"
    if subdomain:
        cmd += f" --subdomain {subdomain}"
    if print_requests:
        cmd += " --print-requests"
    return cmd


def extract_tunnel_url(output: str) -> str | None:
    """Extract the tunnel URL from localtunnel output."""
    match = re.search(r'your url is:\s*(https?://[^\s]+)', output)
    if match:
        return match.group(1).strip()
    return None


def start_tunnel(port: int = 8000, subdomain: str | None = None,
                 print_requests: bool = False) -> subprocess.Popen:
    """
    Start a localtunnel process and return the subprocess handle.

    Uses shell=True on Windows to properly handle .cmd batch files.
    """
    cmd = build_npx_command(port, subdomain, print_requests)

    # On Windows, use shell=True to handle .cmd files (npx.cmd)
    # On Unix, shell=True is also fine for npx
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        shell=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )

    return proc


def wait_for_url(proc: subprocess.Popen, timeout: int = 15) -> str | None:
    """
    Read the tunnel process output until we find the URL.

    Args:
        proc: The localtunnel subprocess
        timeout: Maximum seconds to wait for the URL

    Returns:
        The tunnel URL string, or None if not found
    """
    start_time = time.time()
    url = None

    while time.time() - start_time < timeout:
        # Check if process died
        if proc.poll() is not None:
            remaining = proc.stdout.read() if proc.stdout else ""
            url = extract_tunnel_url(remaining)
            if url:
                return url
            print(f"[tunnel] ERROR: localtunnel exited unexpectedly (code {proc.returncode})",
                  file=sys.stderr)
            return None

        # Read available output (non-blocking via short timeout)
        if proc.stdout:
            line = proc.stdout.readline()
            if line:
                line = line.rstrip()
                print(f"  [tunnel] {line}")
                url = extract_tunnel_url(line)
                if url:
                    return url

        time.sleep(0.1)

    # Timeout: try reading any remaining buffered output
    if proc.stdout:
        remaining = ""
        try:
            while True:
                chunk = proc.stdout.read(1)
                if not chunk:
                    break
                remaining += chunk
        except:  # noqa: E722
            pass
        url = extract_tunnel_url(remaining)
        if url:
            return url

    print(f"[tunnel] WARNING: Could not detect tunnel URL within {timeout}s timeout.",
          file=sys.stderr)
    return None


# ── Render Tunnel Gateway Registration ──────────────────────────────────
# The tunnel URL is automatically reported to the Render-hosted app so it
# can dynamically route task submissions to the local factory gateway.
# This is a best-effort, fire-and-forget call — failures are logged but
# never block the tunnel lifecycle.

RENDER_APP_URL = os.environ.get(
    "MANEKI_RENDER_APP_URL",
    "https://maneki-ai.onrender.com"
)
TUNNEL_REPORT_ENDPOINT = "/api/config/tunnel-gateway"


def report_tunnel_url_to_render(tunnel_url: str) -> None:
    """
    Best-effort POST of the acquired tunnel URL to the Render-hosted app.

    The Render app stores this address and uses it to route task submissions
    to the local factory gateway.  This call is fire-and-forget: any network
    or HTTP error is silently logged and never raises.
    """
    endpoint = f"{RENDER_APP_URL.rstrip('/')}{TUNNEL_REPORT_ENDPOINT}"
    payload = json.dumps({"tunnel_gateway_url": tunnel_url}).encode("utf-8")
    try:
        req = Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urlopen(req, timeout=10)
        print(f"[tunnel] ✅ Tunnel gateway reported to Render — HTTP {resp.status}")
        resp.close()
    except URLError as e:
        print(f"[tunnel] ⚠️  Render unreachable ({e.reason}); tunnel still active.")
    except Exception as e:
        print(f"[tunnel] ⚠️  Failed to report tunnel URL to Render: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Maneki-AI Local Tunnel — Expose localhost via public HTTPS URL"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=8000,
        help="Local port to tunnel (default: 8000)"
    )
    parser.add_argument(
        "--subdomain", "-s", type=str, default=None,
        help="Request a specific subdomain (e.g., 'maneki-ai-factory')"
    )
    parser.add_argument(
        "--print-requests", "-r", action="store_true",
        help="Print basic request info"
    )
    parser.add_argument(
        "--timeout", "-t", type=int, default=15,
        help="Seconds to wait for tunnel URL (default: 15)"
    )
    args = parser.parse_args()

    print(f"[tunnel] Starting localtunnel for localhost:{args.port}...")
    proc = start_tunnel(
        port=args.port,
        subdomain=args.subdomain,
        print_requests=args.print_requests,
    )

    url = wait_for_url(proc, timeout=args.timeout)

    if url:
        # Automatically report the tunnel URL to Render (best-effort)
        report_tunnel_url_to_render(url)

        print()
        print("=" * 60)
        print(f"  🌐 Maneki-AI Tunnel Active!")
        print(f"  🔗 Public URL: {url}")
        print(f"  🎯 Forwarding to: http://localhost:{args.port}")
        print("=" * 60)
        print()
        sys.stdout.flush()

        # Keep the tunnel alive — forward output to stdout
        try:
            while True:
                if proc.poll() is not None:
                    print(f"[tunnel] Tunnel closed (exit code {proc.returncode}).",
                          file=sys.stderr)
                    break
                if proc.stdout:
                    line = proc.stdout.readline()
                    if line:
                        print(f"  [tunnel] {line.rstrip()}")
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[tunnel] Tunnel shutdown requested.")
    else:
        print("[tunnel] Failed to establish tunnel.", file=sys.stderr)
        # Kill the orphaned process
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        sys.exit(1)


if __name__ == "__main__":
    main()
