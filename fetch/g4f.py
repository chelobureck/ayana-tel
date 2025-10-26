import g4f
from typing import Optional, Dict, Any, List
import json
import asyncio


async def get_ai_response(
    user_message: str,
    conversation_id: str,
    context: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Получает ответ от AI модели используя g4f.
    Использует контекст из Redis если доступен.
    """
    # Подготовка контекста
    messages = []
    
    if context:
        for msg in context[-10:]:  # Используем последние 10 сообщений
            role = "user" if msg.get("sender") == "user" else "assistant"
            messages.append({
                "role": role,
                "content": msg.get("text", "")
            })
    
    # Добавляем текущее сообщение
    messages.append({
        "role": "user",
        "content": user_message
    })
    
    try:
        # Используем асинхронный вызов через asyncio.to_thread для совместимости
        loop = asyncio.get_event_loop()
        
        # В g4f используется sync API, оборачиваем в executor
        def _call_g4f():
            # Пробуем разные модели и провайдеры
            models_to_try = [
                ("gpt-4", None),
                ("gpt-3.5-turbo", None),
                ("llama2", None),
            ]
            
            last_error = None
            for model_name, provider in models_to_try:
                try:
                    if provider:
                        response = g4f.ChatCompletion.create(
                            model=model_name,
                            messages=messages,
                            provider=provider
                        )
                    else:
                        response = g4f.ChatCompletion.create(
                            model=model_name,
                            messages=messages
                        )
                    
                    # Проверяем что ответ не None
                    if response:
                        return response
                except Exception as e:
                    last_error = e
                    continue
            
            # Если все попытки провалились, пробуем без указания модели
            try:
                response = g4f.ChatCompletion.create(
                    messages=messages
                )
                if response:
                    return response
            except:
                pass
            
            raise last_error or Exception("Не удалось получить ответ от AI")
        
        response = await loop.run_in_executor(None, _call_g4f)
        
        # response может быть итератором или строкой
        if hasattr(response, '__iter__') and not isinstance(response, str):
            # Если это итератор, собираем результат
            full_response = ""
            for chunk in response:
                if isinstance(chunk, str):
                    full_response += chunk
                else:
                    full_response += str(chunk)
            return full_response
        else:
            return str(response)
    
    except Exception as e:
        # Fallback на базовый ответ
        return f"Извините, произошла ошибка при обработке вашего запроса. Попробуйте переформулировать вопрос. Ошибка: {str(e)[:100]}"


def format_conversation_context(
    context: List[Dict[str, Any]]
) -> str:
    """
    Форматирует контекст для отправки в AI модель.
    """
    formatted = []
    for msg in context:
        sender = msg.get("sender", "unknown")
        text = msg.get("text", "")
        formatted.append(f"{sender}: {text}")
    
    return "\n".join(formatted)

