from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    VERSION: str
    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: str
    class Config:
        env_file = ".env"

settings = Settings()
