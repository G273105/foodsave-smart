"""Send demonstration readings using the agreed ESP32 payload."""

import argparse
import json
import math
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


def make_payload(device_id, temperature, sensor_error=False):
    if device_id not in ("simulator-01", "esp32-01"):
        raise ValueError("Unsupported device identifier")
    if not sensor_error and (
        not math.isfinite(temperature) or not -50 <= temperature <= 100
    ):
        raise ValueError("Temperature must be finite and between -50 and 100 Celsius")
    return {
        "id": device_id,
        "temperature": None if sensor_error else temperature,
        "sensor_status": "error" if sensor_error else "ok",
    }


def send_reading(url, token, payload):
    request = Request(
        url,
        data=json.dumps(payload, allow_nan=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        if response.status != 201:
            raise ValueError(f"Expected HTTP 201, received HTTP {response.status}")
        result = json.loads(response.read())
    reading = result.get("reading", {})
    if any(reading.get(key) != value for key, value in payload.items()):
        raise ValueError("The server acknowledgement does not match the sent reading")
    print("HTTP 201: reading accepted")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=os.getenv("TEMPERATURE_API_URL"))
    parser.add_argument("--temperature", type=float, default=4.6)
    parser.add_argument("--sensor-error", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Print JSON without sending it")
    args = parser.parse_args()
    try:
        payload = make_payload("simulator-01", args.temperature, args.sensor_error)
    except ValueError as exc:
        parser.error(str(exc))
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0
    if not args.url or urlparse(args.url).scheme not in ("http", "https"):
        parser.error("Set TEMPERATURE_API_URL or supply an HTTP(S) --url")
    token = os.getenv("DEVICE_TOKEN", "")
    if not token:
        parser.error("Set DEVICE_TOKEN locally before sending readings")
    try:
        while True:
            try:
                send_reading(args.url, token, payload)
            except HTTPError as exc:
                print(f"Request rejected: HTTP {exc.code}", file=sys.stderr)
                return 1
            except (URLError, TimeoutError, OSError) as exc:
                print(f"Connection failed ({type(exc).__name__}); no acceptance confirmed", file=sys.stderr)
                if args.once:
                    return 1
            except (ValueError, AttributeError) as exc:
                print(f"Invalid acknowledgement: {exc}", file=sys.stderr)
                return 1
            if args.once:
                return 0
            time.sleep(30)
    except KeyboardInterrupt:
        print("Simulator stopped")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
