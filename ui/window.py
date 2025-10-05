import telebot
from telebot import types
from config.settings import get_settings
from ui import buttons as btn
from reply_comand import open_file as of

settings = get_settings()

bot = telebot.TeleBot(settings.TOKEN)


def menu_window(call): # окно главного меню
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    b = btn.for_main_menu()
    bot.send_message(
            chat_id, 
            "_____Главное меню______", 
            reply_markup=b
            )

def help_window(call): # окно помощи
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    b = btn.for_help_menu("back_from_help") # кнопки для меню помощи
    bot.send_message(
            chat_id, 
            of.help_reply(), 
            reply_markup=b,
            parse_mode="HTML"
            )

def about_window(call): # окно о боте
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    b = btn.for_about_menu("back_from_about") # кнопки для меню помощи
    bot.send_message(
            chat_id, 
            of.about_reply(), 
            reply_markup=b,
            parse_mode="HTML"
            )

def gyde_window(call): # окно с гайдом по боту
    try:
        chat_id = call.message.chat.id
    except AttributeError:
        chat_id = call.chat.id

    b = btn.for_gyde_menu("back_from_gyde") # кнопки для меню помощи
    bot.send_message(
            chat_id, 
            of.gyde_reply(), 
            reply_markup=b,
            parse_mode="HTML"
            )

