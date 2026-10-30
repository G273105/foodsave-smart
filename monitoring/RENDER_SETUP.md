# Connect monitoring to Render

Endpoint: https://foodsave-smart.onrender.com/api/temperatures

## Python simulator on Windows

From the repository root in PowerShell, set the private token supplied by the backend developer. Do not copy the PowerShell prompt itself.

```powershell
$env:DEVICE_TOKEN = "YOUR_PRIVATE_TOKEN"
$env:TEMPERATURE_API_URL = "https://foodsave-smart.onrender.com/api/temperatures"
python .\monitoring\simulate.py --temperature 4.0 --once
```

Expected: HTTP 201 and a matching `reading` acknowledgement. Python uses its default verified HTTPS connection. No extra Python package is required. The request timeout is 60 seconds; a timeout does not prove the server did not save the reading. Check the backend before retrying.

After agreeing thresholds with the backend developer, test an out-of-range reading and a sensor failure:

```powershell
python .\monitoring\simulate.py --temperature 12.0 --once
python .\monitoring\simulate.py --sensor-error --once
```

12 C is an example test input, not a locally implemented food-safety threshold. Confirm SAFE/HOLD on the backend after each request. Finally restore a normal reading. A 201 acknowledgement alone does not verify the database or SAFE/HOLD logic. The simulator always identifies itself as `simulator-01`.

## ESP32

1. Download the complete `monitoring/firmware/foodsave_monitor` folder.
2. Keep a backup of your existing private `config.h`. Use the updated `config.example.h` as a template for `config.h` and fill in your existing Wi-Fi credentials, private device token and working DHT GPIO. Do not leave GPIO at -1.
3. The template includes `trusted_roots.h`, the Render HTTPS URL and `MONITOR_ALLOW_LOCAL_HTTP false`. Preserve your display settings in `display_options.h` and TFT_eSPI setup.
4. Compile and upload `foodsave_monitor.ino`. Open Serial Monitor at 115200 baud.
5. Firmware waits for NTP before TLS and uses CA and hostname verification. Never add `setInsecure()`.
6. Expected: Sensor OK, Wi-Fi Connected, Server Accepted, HTTP 201. Humidity remains local; only id, temperature and sensor_status are transmitted. Sensor errors send temperature null.

`trusted_roots.h` contains public ISRG, Google Trust Services and DigiCert roots from the build machine's Mozilla-derived system trust store. This is a small trust store, not a claim about the current Render certificate issuer. If the server chain does not terminate at one of these roots, verification fails; obtain the required root from the CA's official repository, verify its fingerprint independently and update the header. Do not replace it with an unverified certificate or disable TLS checks. Public CA certificates are safe to commit. Private tokens and config.h are not.

## Troubleshooting and validation limits

- Waiting for NTP before TLS: confirm internet access and NTP availability.
- HTTPS CA missing: check config.h and trusted_roots.h.
- HTTP 401/403: confirm the private token with the backend developer.
- HTTP 404: confirm the endpoint path.
- Invalid acknowledgement: capture the response structure without credentials and compare it with the agreed `reading` contract.
- No response: check DNS, network access, TLS trust and server availability.

Six local Python tests passed during preparation. The firmware was not compiled in this environment (Arduino CLI unavailable). Authenticated Render requests, its live certificate chain, database persistence, SAFE/HOLD transitions and physical ESP32 operation remain to be verified on the device/network with the private token.

## History and Connection screens

History stores up to 121 samples in RAM (nominally 60 minutes at 30-second intervals). Tap the History heading to switch temperature/humidity. Each view shows minimum, average, maximum and valid/error counts for the visible hour. Failed readings and long measurement pauses interrupt the graph. No food-safety judgement is calculated on the device. Restarting clears this history; this is not a download of database history.

Connection shows the device ID, Wi-Fi state, local IP, RSSI, server hostname, configured transport/CA, NTP state, whether a token is present (never its value), HTTP result and last accepted reading/age. CA configured does not itself mean a TLS handshake succeeded. Accepted still requires HTTP 201 with the matching reading acknowledgement.

Touch navigation requires board-specific calibration: preserve your known working `MONITOR_TOUCH_CALIBRATION` and `MONITOR_TOUCH_CALIBRATED` settings. With calibration disabled, use Serial Monitor: `h` Home, `g` History, `c` Connection, `t` temperature history, `u` humidity history. The layout targets landscape displays of at least 480 x 320 pixels.

Device acceptance checks still required: switch all tabs; switch history metrics; verify valid/failed readings and statistics; disconnect/reconnect Wi-Fi; verify no credential appears; confirm HTTP 201 and last-accepted age; restart and confirm RAM history clears. Python tests do not validate these display behaviours.
