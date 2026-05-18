from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()

@router.get("/config-check")
def config_check():

    return {
        "telegram_configured":
            bool(settings.TELEGRAM_TOKEN)
    }
