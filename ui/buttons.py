from telebot import types

def help_button(): # кнопка помощи
    return types.InlineKeyboardButton("Помощь", callback_data="help")

def about_button(): # кнопка о боте
    return types.InlineKeyboardButton("О боте", callback_data="about")

def main_menu_button(): # кнопка главного меню
    return types.InlineKeyboardButton("Главное меню", callback_data="main_menu")

def back_button(where: str="back"): # кнопка назад, куда вернуться определяется параметром where
    return types.InlineKeyboardButton("Назад", callback_data=where)

def contact_button(): # кнопка связаться с разработчиком
    return types.InlineKeyboardButton("Связаться с разработчиком", url="https://t.me/cheloberockk")

def gyde_button(): # кнопка руководство по боту
    return types.InlineKeyboardButton("Руководство по боту", callback_data="gyde")

def for_main_menu(): #кнопки для главного меню 
    b = types.InlineKeyboardMarkup()
    b.row(help_button(), about_button())
    b.row(contact_button(), gyde_button())
    return b

def for_help_menu(back_from_where: str): # кнопки для меню помощи
    b = types.InlineKeyboardMarkup()
    b.row(back_button(back_from_where))
    b.row(main_menu_button())
    return b

def for_about_menu(back_from_where: str): # кнопки для меню о боте
    b = types.InlineKeyboardMarkup()
    b.row(back_button(back_from_where))
    b.row(main_menu_button())
    return b

def for_gyde_menu(back_from_where: str): # кнопки для меню с гайдом по боту
    b = types.InlineKeyboardMarkup()
    b.row(help_button())
    b.row(back_button(back_from_where))
    b.row(main_menu_button())
    return b

