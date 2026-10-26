
import getpass
import requests


API_URL = "https://foodsave-smart.onrender.com/api/temperatures"


def main():
    token = getpass.getpass("Enter Render DEVICE_TOKEN: ")

    payload = {
        "id": "simulator-01",
        "temperature": 4.6,
        "sensor_status": "ok"
    }

    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=60
        )

        print("HTTP status:", response.status_code)
        print("Server response:", response.text)

    except requests.RequestException as error:
        print("Connection error:", error)


if __name__ == "__main__":
    main()
