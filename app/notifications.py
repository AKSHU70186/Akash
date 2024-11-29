import aiohttp
from typing import Dict, Any
import json
import logging
import datetime
class WebhookNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_notification(self, event_type: str, data: Dict[str, Any]):
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status not in (200, 201, 202):
                        logging.error(f"Webhook notification failed: {await response.text()}")
                    return response.status
            except Exception as e:
                logging.error(f"Error sending webhook notification: {str(e)}")
                return None 