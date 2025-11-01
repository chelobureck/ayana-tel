from __future__ import annotations
from typing import List, Dict, Any, Optional
import asyncio

import g4f
from g4f import Messages

from service.chat_service import ChatService


class AiService:
    @staticmethod
    async def generate_reply(
        user_message: str,
        conversation_id: str,
        context: Optional[List[Dict[str, Any]]],
        system_prompt: str,
    ) -> str:
        # Формируем сообщения для модели
        messages: Messages = []
        messages.append({"role": "system","content": f"{system_prompt}"})

        if context:
            for msg in context[-10:]:
                role = "user" if msg.get("sender") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("text", "")})

        messages.append({"role": "user", "content": user_message})

        loop = asyncio.get_event_loop()

        def _call_models_chain() -> str:
            # Последовательность моделей для пробы
            models_to_try = [
                ("gpt-4", None),
                ("gpt-4o", None),
                ("gpt-4o-mini", None),
                ("gpt-3.5-turbo", None),
                ("llama2", None),
            ]
            last_error: Optional[Exception] = None
            for model, provider in models_to_try:
                try:
                    if provider:
                        resp = g4f.ChatCompletion.create(model=model, messages=messages, provider=provider)
                    else:
                        resp = g4f.ChatCompletion.create(model=model, messages=messages)
                    if resp:
                        if hasattr(resp, "__iter__") and not isinstance(resp, str):
                            text = "".join([chunk if isinstance(chunk, str) else str(chunk) for chunk in resp])
                        else:
                            text = str(resp)
                        return text
                except Exception as e:  # noqa: BLE001
                    last_error = e
                    continue
            if last_error:
                raise last_error
            return "Извини, сейчас я перегружена. Попробуй повторить вопрос позже."

        try:
            response = await loop.run_in_executor(None, _call_models_chain)
            return response
        except Exception as e:  # noqa: BLE001
            return (
                "Мне не удалось получить ответ от ИИ. "
                "Попробуй переформулировать вопрос или повторить позже."
            )
