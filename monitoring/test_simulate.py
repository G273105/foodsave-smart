"""Check sender behaviour against a real local HTTP listener."""

import json
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
from urllib.error import HTTPError

from simulate import make_payload, send_reading


class SenderTests(unittest.TestCase):
    def test_error_reading_has_no_temperature(self):
        self.assertEqual(make_payload("simulator-01", 4.6, True), {
            "id": "simulator-01", "temperature": None, "sensor_status": "error"
        })

    def test_non_finite_reading_is_rejected(self):
        for value in (float("nan"), float("inf"), -51, 101):
            with self.assertRaises(ValueError):
                make_payload("simulator-01", value)

    def test_http_authentication_payload_and_rejection(self):
        captured = []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                captured.append((self.path, self.headers.get("Content-Type"), body))
                authorised = self.headers.get("Authorization") == "Bearer local-test-value"
                self.send_response(201 if authorised else 401)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"reading": body}).encode())

            def log_message(self, *args):
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f"http://127.0.0.1:{server.server_port}/api/temperatures"
        payload = make_payload("simulator-01", 4.6)
        try:
            with redirect_stdout(StringIO()):
                send_reading(url, "local-test-value", payload)
            self.assertEqual(captured[0], ("/api/temperatures", "application/json", payload))
            with self.assertRaises(HTTPError) as rejected:
                send_reading(url, "wrong-value", payload)
            self.assertEqual(rejected.exception.code, 401)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
