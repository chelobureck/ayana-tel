"""
Запуск FastAPI сервера
Используйте этот скрипт для запуска REST API
"""
import uvicorn
from config.settings import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )

