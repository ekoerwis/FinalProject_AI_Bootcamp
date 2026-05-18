from fastapi import FastAPI
from app.api.routes import router
from app.config.settings import settings
from app.api.debug import router as debug_router

app = FastAPI(
    title=settings.APP_NAME,
    Version=settings.VERSION
)

app.include_router(router)
app.include_router(debug_router)

@app.get("/")
def root():
    return {
	"message": f"{settings.APP_NAME} running"
    }

@app.get("/health")
def health():
    return {
	"status": "ok",
	"app": settings.APP_NAME,
	"version": settings.VERSION
    }
