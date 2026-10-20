"""Verify the monitoring contract against a local copy of Laurentiu's Flask app.

Usage: python monitoring/verify_backend.py --backend backend/app.py
Uses an ephemeral local token and an isolated in-memory app instance.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import secrets
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from werkzeug.serving import WSGIRequestHandler, make_server
from simulate import make_payload, send_reading


class QuietHandler(WSGIRequestHandler):
    def log(self, *args, **kwargs):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", type=Path, required=True)
    args = parser.parse_args()
    if not args.backend.is_file():
        parser.error("The backend file is not available; fetch or check out PR #3 first")
    token = secrets.token_urlsafe(24)
    os.environ["DEVICE_TOKEN"] = token
    spec = importlib.util.spec_from_file_location("monitoring_backend_check", args.backend)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    server = make_server("127.0.0.1", 0, module.app, request_handler=QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    failures = []

    def request(path, payload=None, authorised=True):
        headers = {"Authorization": f"Bearer {token if authorised else 'invalid'}"}
        data = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode()
        try:
            with urlopen(Request(base + path, data=data, headers=headers), timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as response:
            return response.code, json.loads(response.read())

    def check(name, passed, detail=""):
        print(f"{'PASS' if passed else 'FAIL'}: {name} {detail}")
        if not passed:
            failures.append(name)

    try:
        status, _ = request("/api/health")
        check("Health endpoint", status == 200)
        send_reading(base + "/api/temperatures", token, make_payload("simulator-01", 4.6))
        status, result = request("/api/fridge/status")
        check("Latest simulator reading is retrievable", status == 200 and
              result["latest_readings"]["simulator-01"]["temperature"] == 4.6)
        check("Receipt timestamp is present", bool(result["latest_readings"]["simulator-01"]["received_at"]))
        status, _ = request("/api/temperatures", make_payload("simulator-01", 4.6), False)
        check("Invalid token rejected", status == 401)
        status, _ = request("/api/temperatures", make_payload("simulator-01", 0, True))
        check("Sensor error accepted", status == 201)
        status, _ = request("/api/temperatures", make_payload("esp32-01", 4.6))
        check("Physical device payload accepted", status == 201)
        status, _ = request("/api/temperatures", {"id": "unknown", "temperature": 4.6, "sensor_status": "ok"})
        check("Unknown device rejected", status == 400)
        status, _ = request("/api/temperatures", {"id": "simulator-01", "temperature": None, "sensor_status": "ok"})
        check("Missing normal temperature rejected", status == 400)
        status, _ = request("/api/temperatures", {"id": "simulator-01", "temperature": 4.6, "sensor_status": "error"})
        check("Error status with numeric temperature rejected", status == 400, f"(HTTP {status})")
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
    print(f"Contract checks completed: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
