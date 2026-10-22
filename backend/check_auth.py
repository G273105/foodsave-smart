
import requests

# Test the API without an authentication token.
url = "http://127.0.0.1:5000/api/temperatures"

data = {
    "device_id": "simulator-01",
    "temperature": 4.6
}

try:
    response = requests.post(url, json=data, timeout=10)

    print("=== FoodSave Smart - Authentication Test ===")
    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 401:
        print("SUCCESS: Unauthorized access was blocked.")
    else:
        print("WARNING: Unexpected authentication response.")

except requests.RequestException as error:
    print(f"CONNECTION FAILED: {error}")
