import requests
from app.config.settings import settings

def send_telegram_message(
    text: str
):

    url = (
        f"https://api.telegram.org/"
        f"bot{settings.TELEGRAM_TOKEN}"
        f"/sendMessage"
    )

    payload = {
        "chat_id":
            settings.TELEGRAM_CHAT_ID,

        "text":
            text
    }

    response = requests.post(
        url,
        json=payload
    )

    return response.json()
