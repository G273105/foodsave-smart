
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load the device authentication token.
load_dotenv(Path(__file__).resolve().parent / ".env")

# API endpoint and authentication.
url = "http://127.0.0.1:5000/api/temperatures"

headers = {
    "Authorization": f"Bearer {os.getenv('DEVICE_TOKEN')}"
}

# Simulate a safe temperature reading.
data = {
    "id": "simulator-01",
    "temperature": 4.6,
    "sensor_status": "ok"
}

try:
    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=10
    )

    print("=== FoodSave Smart - Temperature Test ===")
    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 201:
        print("SUCCESS: Temperature saved successfully.")
    else:
        print("WARNING: Temperature was not accepted.")

except requests.RequestException as error:
    print(f"CONNECTION FAILED: {error}")
