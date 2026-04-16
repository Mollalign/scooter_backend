import httpx

from app.core.config import settings


class ChapaClient:
    def __init__(self):
        self.base_url = settings.CHAPA_BASE_URL
        self.secret_key = settings.CHAPA_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self,
        amount: float,
        tx_ref: str,
        callback_url: str,
        return_url: str,
        customer_name: str,
        customer_phone: str,
    ) -> dict:
        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url,
            "first_name": customer_name.split()[0] if customer_name else "",
            "last_name": customer_name.split()[-1] if customer_name and len(customer_name.split()) > 1 else "",
            "phone_number": customer_phone,
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{self.base_url}/transaction/initialize",
                json=payload,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    async def verify_transaction(self, tx_ref: str) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.base_url}/transaction/verify/{tx_ref}",
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
