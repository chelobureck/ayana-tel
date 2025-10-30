import telebot
from telebot import types 
import asyncio
import threading
from config.settings import get_settings
from ui import (
    buttons as btn,
    window as win
)
from reply_comand import open_file as of
from service.chat_service import ChatService
from service.ai_service import AiService
from utils.redis_client import get_messages
from sqlalchemy.ext.asyncio import AsyncSession
from models.base import async_session
from models.user import User
from sqlalchemy import select


settings = get_settings()

bot = telebot.TeleBot(settings.TOKEN)

# Единый фоновый event loop для всех async операций (DB/Redis/AI)
_BACKGROUND_LOOP = asyncio.new_event_loop()

def _loop_worker(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()

_loop_thread = threading.Thread(target=_loop_worker, args=(_BACKGROUND_LOOP,), daemon=True)
_loop_thread.start()


def run_async(coro):
    """Выполняет coroutine в едином фоновом event loop (без конфликтов циклов)."""
    fut = asyncio.run_coroutine_threadsafe(coro, _BACKGROUND_LOOP)
    return fut.result()


async def get_or_create_user(telegram_id: int, username: str | None, first_name: str | None) -> User:
    """Получает пользователя из БД или создает нового"""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        
        if user is None:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        
        return user


@bot.message_handler(commands=['start'])
def start(message):
    b2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b2.row(types.KeyboardButton("Помощь"), types.KeyboardButton("О боте"))
    b2.row(types.KeyboardButton("Меню"))
    
    bot.send_message(
        message.chat.id, 
        "Привет, я Ayana. Я создана для помощи твоему ребенку с темами, которые могут быть непонятны. Задай мне вопрос!",
        reply_markup=b2
    )
    
    # Создаем пользователя в БД
    user = run_async(get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    ))


@bot.message_handler(commands=['menu'])
def menu(message):
    win.menu_window(message)


@bot.message_handler(commands=['help'])
def help(message):
    win.help_window(message)


@bot.message_handler(commands=['about'])
def about(message):
    win.about_window(message)


@bot.message_handler(commands=['gyde'])
def gyde(message):
    win.gyde_window(message)


@bot.message_handler(commands=['set_name'])
def set_name(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи имя через пробел: /set_name Алиса")
        return
    name = parts[1].strip()
    async def save_name():
        async with async_session() as session:
            user = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
            child = await ChatService.extract_and_save_child_info(session, user, f"имя: {name}")
            await session.commit()
    run_async(save_name())
    bot.send_message(message.chat.id, f"Имя ребенка сохранено: {name}")


@bot.message_handler(commands=['set_age'])
def set_age(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи возраст через пробел: /set_age 8")
        return
    try:
        age = int(parts[1].strip())
    except Exception:
        bot.send_message(message.chat.id, "Возраст должен быть числом, например: /set_age 8")
        return
    async def save_age():
        async with async_session() as session:
            user = await get_or_create_user(message.from_user.id, message.from_user.username, message.from_user.first_name)
            child = await ChatService.extract_and_save_child_info(session, user, f"возраст: {age} лет")
            await session.commit()
    run_async(save_age())
    bot.send_message(message.chat.id, f"Возраст ребенка сохранен: {age}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Обработка текстовых сообщений пользователя"""
    
    # Проверяем, не является ли это кнопкой меню
    if message.text in ["Помощь", "О боте", "Меню"]:
        one_click(message)
        return
    
    # Получаем или создаем пользователя
    user = run_async(get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    ))
    
    conversation_id = f"chat_{message.from_user.id}"
    
    # Показываем индикатор "печатает"
    bot.send_chat_action(message.chat.id, 'typing')
    
    async def process_message():
        # Получаем контекст из Redis
        context = await ChatService.get_context(conversation_id, limit=10)
        
        # Сохраняем сообщение пользователя в БД
        async with async_session() as session:
            msg = await ChatService.save_message_db(
                session, 
                conversation_id, 
                "user", 
                message.text,
                user_id=user.id
            )
            
            # Пушим в Redis
            await ChatService.push_to_redis(conversation_id, "user", message.text, meta={"id": msg.id})
            
            await session.commit()
        # Формируем system prompt с учетом профиля ребенка
        async with async_session() as session:
            child = await ChatService.get_child_info(session, user.id)
            system_prompt = ChatService.build_system_prompt(child)

        # Получаем ответ от AI через сервис
        ai_response = await AiService.generate_reply(
            user_message=message.text,
            conversation_id=conversation_id,
            context=context,
            system_prompt=system_prompt,
        )
        
        # Сохраняем ответ бота в БД
        async with async_session() as session:
            bot_msg = await ChatService.save_message_db(
                session,
                conversation_id,
                "bot",
                ai_response,
                user_id=user.id
            )
            
            # Пушим ответ в Redis
            await ChatService.push_to_redis(conversation_id, "bot", ai_response, meta={"id": bot_msg.id})
            
            await session.commit()
        
        return ai_response
    
    # Получаем ответ от AI
    response = run_async(process_message())
    
    # Отправляем ответ пользователю
    bot.send_message(message.chat.id, response)


def one_click(messaga):  # кнопки для основного меню
    if messaga.text == "Помощь":
        win.help_window(messaga)
    elif messaga.text == "О боте":
        win.about_window(messaga)
    elif messaga.text == "Меню":
        win.menu_window(messaga)
    else:
        bot.send_message(messaga.chat.id, "Пожалуйста, используйте кнопки для навигации по боту.", )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # открытие меню помощи по кнопке помощь
    if call.data == "help":
        win.help_window(call)
    elif call.data == "about":
        win.about_window(call)
    # открытие главного меню по кнопке главное меню
    elif call.data == "main_menu":
        win.menu_window(call)
    # открытие главного меню из меню помощи
    elif call.data == "back_from_help":
        win.menu_window(call)
    # открытие главного меню из меню о боте
    elif call.data == "back_from_about":
        win.menu_window(call)
    # открытие главного меню из меню с гайда по боту
    elif call.data == "back_from_gyde":
        win.menu_window(call)
    # открытие меню с гайдом по боту
    elif call.data == "gyde":
        win.gyde_window(call)


if __name__ == '__main__':
    print("Бот Ayana запущен!")
    bot.polling(none_stop=True)