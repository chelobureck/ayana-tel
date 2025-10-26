"""
FastAPI application для REST API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import get_settings
from routers import chat

settings = get_settings()

app = FastAPI(
    title=settings.API_TITLE,
    version="1.0.0",
    description="REST API для бота Ayana"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(chat.router)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Ayana Bot API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

