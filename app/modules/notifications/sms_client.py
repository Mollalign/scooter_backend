import httpx

from app.core.config import settings


class SMSClient:
    def __init__(self):
        self.api_url = settings.SMS_API_URL
        self.api_key = settings.SMS_API_KEY
        self.sender_name = settings.SMS_SENDER_NAME

    async def send_sms(self, phone: str, message: str) -> dict:
        payload = {
            "to": phone,
            "message": message,
            "sender": self.sender_name,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
