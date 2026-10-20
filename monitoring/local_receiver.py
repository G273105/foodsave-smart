"""Local test receiver (loopback by default), not the FoodSave Smart production backend.

Run with DEVICE_TOKEN configured locally. Data lives in memory only.
"""

import argparse
from datetime import datetime, timezone
import hmac
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
import os


def receiver_handler(token):
    latest = {}

    class Receiver(BaseHTTPRequestHandler):
        def reply(self, code, body):
            data = json.dumps(body, allow_nan=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/api/health":
                self.reply(200, {"status": "ok", "mode": "LOCAL TEST RECEIVER"})
            elif self.path == "/api/fridge/status":
                self.reply(200, {"mode": "LOCAL TEST RECEIVER", "latest_readings": latest})
            else:
                self.reply(404, {"error": "Unknown endpoint"})

        def do_POST(self):
            if self.path != "/api/temperatures":
                self.reply(404, {"error": "Unknown endpoint"})
                return
            supplied = self.headers.get("Authorization", "").encode()
            if not hmac.compare_digest(supplied, f"Bearer {token}".encode()):
                self.reply(401, {"error": "Invalid device token"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 4096:
                    raise ValueError()
                if self.headers.get_content_type() != "application/json":
                    raise ValueError()
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict) or set(data) != {"id", "temperature", "sensor_status"}:
                    raise ValueError()
                if data["id"] not in ("simulator-01", "esp32-01"):
                    raise ValueError()
                status, temperature = data["sensor_status"], data["temperature"]
                if status == "ok":
                    if type(temperature) not in (int, float) or not math.isfinite(temperature) or not -50 <= temperature <= 100:
                        raise ValueError()
                elif status != "error" or temperature is not None:
                    raise ValueError()
            except (ValueError, TypeError, UnicodeError):
                self.reply(400, {"error": "Invalid monitoring payload"})
                return
            reading = {**data, "received_at": datetime.now(timezone.utc).isoformat()}
            latest[data["id"]] = reading
            self.reply(201, {"mode": "LOCAL TEST RECEIVER", "reading": reading})
            print(f"Accepted {data['id']}: {status}, temperature={temperature}", flush=True)

        def log_message(self, *args):
            # Do not log headers or credentials.
            pass

    return Receiver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--host", default="127.0.0.1", help="Use 0.0.0.0 for an authorised local Wi-Fi device test")
    args = parser.parse_args()
    token = os.getenv("DEVICE_TOKEN", "")
    if not token:
        parser.error("Set DEVICE_TOKEN locally before starting the receiver")
    with HTTPServer((args.host, args.port), receiver_handler(token)) as server:
        print(f"LOCAL TEST RECEIVER: http://{args.host}:{server.server_port}", flush=True)
        if args.host == "0.0.0.0":
            print("LAN listening enabled: connect using this PC LAN IPv4, not 0.0.0.0 or 127.0.0.1.", flush=True)
        print("In-memory data only. No SQLite, food rules or production backend. Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("Receiver stopped")


if __name__ == "__main__":
    main()
