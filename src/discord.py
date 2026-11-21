import os
import logging
import requests

logger = logging.getLogger("doctor")

def send_discord_alert(message: str) -> None:
    """Send an alert message to Discord via webhook.
    
    Reads DISCORD_WEBHOOK_URL from environment variables.
    Fails gracefully without raising exceptions if the webhook is unset or the request fails.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not webhook_url:
        logger.debug("DISCORD_WEBHOOK_URL is not set. Skipping Discord notification.")
        return

    payload = {"content": message}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.error("Failed to send Discord alert: %s", exc)
