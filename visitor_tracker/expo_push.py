import requests

def send_push_notification(token: str, title: str, body: str, data: dict = None):
    message = {
        "to": token,
        "sound": "default",
        "title": title,
        "body": body,
        "data": data or {}
    }
    response = requests.post("https://exp.host/--/api/v2/push/send", json=message)
    print("Expo status:", response.status_code)
    print("Expo response:", response.text)
    return response.json()