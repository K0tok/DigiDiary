import telebot
from functions import get_groups
from DataBase import select_groups

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("/schedule")


simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)

keyboard_groups = telebot.types.InlineKeyboardMarkup(row_width=2)
groups = select_groups()
buttons = []
for group in groups:
    group_name = group['name']
    
    # Проверяем, принадлежит ли группа пользователю
    if group_name in ['Т-143901-ИСТ', 'Т-233901-ИСТ']:              # ДОБАВИТЬ ПРОСМОТР ГРУПП ПОЛЬЗОВАТЕЛЯ
        button_text = f"<< {group_name} >>" 
    else:
        button_text = group_name
    
    button = telebot.types.InlineKeyboardButton(
        text=button_text,
        callback_data=f"group_{group['name']}"
    )
    buttons.append(button)

keyboard_groups.add(*buttons)
