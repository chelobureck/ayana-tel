import telebot
from telebot import types 
from config.settings import get_settings
from ui import (
    buttons as btn,
    window as win
)
from reply_comand import open_file as of



settings = get_settings()

bot = telebot.TeleBot(settings.TOKEN)



@bot.message_handler(commands=['start'])
def start(message):
    b = types.InlineKeyboardMarkup()
    b.row(btn.help_button(), btn.about_button())
    b.row(btn.main_menu_button())
    bot.send_message(
        message.chat.id, 
        "Привет, я Ayana. Я создана для помощи вашему ребенку с темами, кторые им могут быть непонятны.", 
        reply_markup=b # кнопки для стартового меню
        )

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



bot.polling(none_stop=True)