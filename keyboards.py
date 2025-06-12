import requests
import telebot
from Functions import get_groups, is_numerator
from DataBase import select_groups, select_user_groups, select_union_groups, select_union

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("🗓️ Моё расписание", "📅 Расписание на сегодня")
keyboard_commands.row("📚 Расписание занятий НТИ", "📖 Дневник")
keyboard_commands.row("👤 Мой профиль")

keyboard_commands_chat = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands_chat.row("📚 Расписание занятий НТИ", "📖 Дневник")
keyboard_commands_chat.row("⚙️ Параметры", "➕ Прикрепить меня")
keyboard_commands_chat.row("👤 Профиль группы")

simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)

keyboard_profile = telebot.types.InlineKeyboardMarkup(row_width=1)
keyboard_profile.add(telebot.types.InlineKeyboardButton(text="✏️ Изменить имя", callback_data="changeMyName_user"))

keyboard_profile_chat = telebot.types.InlineKeyboardMarkup(row_width=1)
keyboard_profile_chat.add(telebot.types.InlineKeyboardButton(text="✏️ Изменить название", callback_data="changeMyName_union"))

keyboard_diary_functions = telebot.types.ReplyKeyboardMarkup(True)
keyboard_diary_functions.row("📒 Посмотреть мои ДЗ", "📌 Добавить новое задание")

def create_keyboard_groups(dayType = None, chat_id = None, union_delete = None):
    # Определяем расписание запрошено в беседе или в личных сообщениях
    if chat_id < 0:
        union_id = select_union(chat_id)['id']
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
        
        if dayType == 'today':
            button_callback = f"group_{group['id']}_today_default"
        elif dayType == 'week':
            button_callback = f"group_{group['id']}_week_default"
        else:
            button_callback = f"groupId_{group['id']}_add"

        # Проверяем, принадлежит ли группа пользователю
        if group_id in select_user_groups(user_id):
            button_text = f"▶️ {group_name} ◀️" 
        elif group_id in select_union_groups(union_id):
            button_text = f"▶️ {group_name} ◀️" 
            if union_delete:
                button_callback = f"groupId_{group['id']}_delete"
        else:
            button_text = group_name

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
            button_text = 'Сменить на: Знаменатель'
            button_callback = f"group_{group_id}_week_denominator"
        else:
            button_text = 'Сменить на: Числитель'
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


def create_keyboard_subjects(url, group_names):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        subjects = set()

        def recursive_search(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "n" and isinstance(value, str) and value.strip():
                        subject_name = value.split(" (")[0].split(",")[0].strip()
                        subjects.add(subject_name)
                    else:
                        recursive_search(value)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_search(item)

        if isinstance(group_names, str):
            group_names = [group_names]

        for group_name in group_names:
            group_data = data.get(group_name)
            if group_data:
                for day in group_data:
                    recursive_search(day)

        sorted_subjects = sorted(subjects)

        keyboard_subjects = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(0, len(sorted_subjects), 2):
            row = []
            row.append(sorted_subjects[i])
            if i + 1 < len(sorted_subjects):
                row.append(sorted_subjects[i + 1])
            keyboard_subjects.row(*row)

        return keyboard_subjects

    except Exception as e:
        print(f"Ошибка при получении предметов: {e}")
        return [], None