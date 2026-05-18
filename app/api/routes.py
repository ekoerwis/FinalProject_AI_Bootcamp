import requests
import os
from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.chat_service import process_message
from app.services.telegram_service import (send_telegram_message)
from app.config.settings import settings

router = APIRouter()


@router.get("/status")
def status():
    return {
	"backend": "running",
	"version": "0.1"
    }


@router.post("/chat")
def chat(request: ChatRequest):
    reply = process_message(
        request.message
    )

    return {
	"reply": reply
    }

@router.post("/telegram/webhook")
def telegram_webhook(payload: dict):

    message = payload.get(
        "message",
        {}
    ).get(
        "text",
        ""
    )

    chat_id = payload.get(
        "message",
        {}
    ).get(
        "chat",
        {}
    ).get(
        "id"
    )

    reply = f"Backend received: {message}"

    token = settings.TELEGRAM_TOKEN

    print("TOKEN:", token)
    print("CHAT ID:", chat_id)

    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return {
       "reply": reply
    }

@router.post("/telegram/send")
def send_message():

    response = send_telegram_message(
        "Halo dari backend FastAPI"
    )

    return response
