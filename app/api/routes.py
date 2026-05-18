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
