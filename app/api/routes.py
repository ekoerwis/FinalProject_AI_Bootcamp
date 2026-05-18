from fastapi import APIRouter
from app.models.chat import ChatRequest
from app.services.chat_service import process_message

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
def telegram_webhook(
    payload: dict
):

    message = payload.get(
        "message",
        {}
    ).get(
        "text",
        ""
    )

    reply = process_message(
        message
    )

    return {
       "telegram_reply": reply
    }
