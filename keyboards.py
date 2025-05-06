import telebot
from Functions import get_groups, is_numerator
from DataBase import select_groups, select_user_groups, select_union_groups

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("🗓️ Моё расписание", "📅 Расписание на сегодня")
keyboard_commands.row("📚 Расписание занятий НТИ", "📖 Дневник")
keyboard_commands.row("👤 Мой профиль", "⚙️ Параметры")


simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)


def create_keyboard_groups(dayType = None, chat_id = None):
    # Определяем расписание запрошено в беседе или в личных сообщениях
    if chat_id < 0:
        union_id = chat_id
        user_id = None
    if chat_id > 0:
        user_id = chat_id
        union_id = None
    keyboard_groups = telebot.types.InlineKeyboardMarkup(row_width=2)
    groups = select_groups()
    buttons = []
    for group in groups:
        group_name = group['name']
        group_id = group['id']
        # Проверяем, принадлежит ли группа пользователю
        if group_id in select_user_groups(user_id):
            button_text = f"▶️ {group_name} ◀️" 
        elif group_id in select_union_groups(union_id):
            button_text = f"▶️ {group_name} ◀️" 
        else:
            button_text = group_name
        
        if dayType == 'today':
            button_callback = f"group_{group['id']}_today_default"
        elif dayType == 'week':
            button_callback = f"group_{group['id']}_week_default"
        else:
            button_callback = f"groupId_{group['id']}"

        button = telebot.types.InlineKeyboardButton(
            text=button_text,
            callback_data=button_callback
        )
        buttons.append(button)

    keyboard_groups.add(*buttons)
    return keyboard_groups


def keyboard_numerator(isNumerator, group_id):
    keyboard_numerator = telebot.types.InlineKeyboardMarkup(row_width=1)
    if isNumerator == -1:
        if is_numerator():
            button_text = 'Сменить на: Числитель'
            button_callback = f"group_{group_id}_week_denominator"
        else:
            button_text = 'Сменить на: Знаменатель'
            button_callback = f"group_{group_id}_week_numerator"
    elif isNumerator == 1:
        button_text = 'Сменить на: Числитель'
        button_callback = f"group_{group_id}_week_denominator"
    elif isNumerator == 0:
        button_text = 'Сменить на: Знаменатель'
        button_callback = f"group_{group_id}_week_numerator"
    button = telebot.types.InlineKeyboardButton(
        text=button_text,
        callback_data=button_callback
    )
    keyboard_numerator.add(button)
    return keyboard_numerator