import telebot
from functions import get_groups
from DataBase import select_groups, select_user_groups

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("🗓️ Расписание занятий НТИ", "📅 Расписание на сегодня")
keyboard_commands.row("👤 Мой профиль", "📖 Дневник")


simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)

def create_keyboard_groups(dayType = None, user_id = None):
    keyboard_groups = telebot.types.InlineKeyboardMarkup(row_width=2)
    groups = select_groups()
    buttons = []
    for group in groups:
        group_name = group['name']
        group_id = group['id']
        # Проверяем, принадлежит ли группа пользователю
        if group_id in select_user_groups(user_id):              # ДОБАВИТЬ ПРОСМОТР ГРУПП ПОЛЬЗОВАТЕЛЯ
            button_text = f"<< {group_name} >>" 
        else:
            button_text = group_name
        
        if dayType == 'today':
            button_callback = f"group_{group['name']}_today"
        elif dayType == 'week':
            button_callback = f"group_{group['name']}_week"
        else:
            button_callback = f"groupId_{group['id']}"

        button = telebot.types.InlineKeyboardButton(
            text=button_text,
            callback_data=button_callback
        )
        buttons.append(button)

    keyboard_groups.add(*buttons)
    return keyboard_groups


keyboard_groups_week = telebot.types.InlineKeyboardMarkup(row_width=2)
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
        callback_data=f"group_{group['name']}_week"
    )
    buttons.append(button)

keyboard_groups_week.add(*buttons)

keyboard_groups_today = telebot.types.InlineKeyboardMarkup(row_width=2)
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
        callback_data=f"group_{group['name']}_today"
    )
    buttons.append(button)

keyboard_groups_today.add(*buttons)

keyboard_groups = telebot.types.InlineKeyboardMarkup(row_width=2)
groups = select_groups()
buttons = []
for group in groups:
    button_text = group['name']
    
    button = telebot.types.InlineKeyboardButton(
        text=button_text,
        callback_data=f"groupId_{group['id']}"
    )
    buttons.append(button)

keyboard_groups.add(*buttons)