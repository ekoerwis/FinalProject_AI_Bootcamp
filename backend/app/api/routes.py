import requests
import os
from fastapi.responses import JSONResponse
from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.chat_service import get_response
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
    reply = get_response(
        message=request.message 
    )

    return JSONResponse(
       content={"reply": reply},
       media_type="application/json; charset=utf-8"
    )

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

    reply = get_response(message)

    token = settings.TELEGRAM_TOKEN


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
