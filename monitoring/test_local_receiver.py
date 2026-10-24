"""Exercise simulator and receiver together over HTTP."""

from contextlib import redirect_stdout
from http.server import HTTPServer
from io import StringIO
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from local_receiver import receiver_handler
from simulate import make_payload, send_reading


class ReceiverIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.server = HTTPServer(("127.0.0.1", 0), receiver_handler("test-only-value"))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_normal_then_error_can_be_read_back(self):
        for failed in (False, True):
            payload = make_payload("simulator-01", 4.6, failed)
            with redirect_stdout(StringIO()):
                send_reading(self.base + "/api/temperatures", "test-only-value", payload)
            with urlopen(self.base + "/api/fridge/status") as response:
                reading = json.load(response)["latest_readings"]["simulator-01"]
            for key, value in payload.items():
                self.assertEqual(reading[key], value)
            self.assertIn("received_at", reading)

    def test_wrong_token_rejected(self):
        with self.assertRaises(HTTPError) as error:
            send_reading(self.base + "/api/temperatures", "wrong", make_payload("simulator-01", 4.6))
        self.assertEqual(error.exception.code, 401)

    def test_inconsistent_sensor_error_rejected(self):
        payload = {"id": "simulator-01", "temperature": 4.6, "sensor_status": "error"}
        request = Request(self.base + "/api/temperatures", data=json.dumps(payload).encode(),
                          headers={"Content-Type": "application/json", "Authorization": "Bearer test-only-value"})
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
