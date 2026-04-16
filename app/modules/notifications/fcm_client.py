import httpx

from app.core.config import settings


class FCMClient:
    FCM_SEND_URL = "https://fcm.googleapis.com/fcm/send"

    def __init__(self):
        self.server_key = settings.FCM_SERVER_KEY

    async def send_push(self, fcm_token: str, title: str, body: str, data: dict | None = None) -> dict:
        payload = {
            "to": fcm_token,
            "notification": {
                "title": title,
                "body": body,
            },
        }
        if data:
            payload["data"] = data

        headers = {
            "Authorization": f"key={self.server_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.FCM_SEND_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
