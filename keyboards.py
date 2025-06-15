import requests
import telebot
from Functions import get_groups, is_numerator
from DataBase import select_group, select_groups, select_user_groups, select_union_groups, select_union, select_union_by_id, select_user_unions

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("🗓️ Моё расписание", "📅 Расписание на сегодня")
keyboard_commands.row("📚 Расписание занятий НТИ", "📒 Посмотреть мои ДЗ")
keyboard_commands.row("👤 Мой профиль")

keyboard_commands_chat = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands_chat.row("📚 Расписание занятий НТИ", "📌 Добавить новое задание")
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

keyboard_cancel = telebot.types.ReplyKeyboardMarkup(True)
keyboard_cancel.add(telebot.types.KeyboardButton("❌ Отмена"))

def create_keyboard_isDone(hw, is_done):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_text = "❌ Отменить выполнение" if is_done else "✅ Выполнить"
    keyboard.add(telebot.types.InlineKeyboardButton(button_text, callback_data=f"toggle_hw_{hw['id']}"))
    keyboard.add(telebot.types.InlineKeyboardButton("🗂 В архив", callback_data=f"archive_hw_{hw['id']}"))
    return keyboard

def get_archive_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(telebot.types.InlineKeyboardButton("🗂 Открыть архив", callback_data=f"archive_menu"))
    return keyboard

def get_homework_keyboard(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(
        row_width=1,
        one_time_keyboard=True,
        resize_keyboard=True
    )

    buttons = [telebot.types.KeyboardButton("📚 Все задания")]

    user_unions = select_user_unions(user_id)
    if not user_unions:
        return telebot.types.ReplyKeyboardMarkup()

    for u in user_unions:
        union_id = u['union_id']
        union_data = select_union_by_id(union_id)

        if not union_data:
            continue

        union_name = union_data.get('name', f'Объединение {union_id}')

        # Получаем ID групп, связанных с объединением
        group_ids = select_union_groups(union_id)
        group_names = []

        for g in group_ids:
            group_data = select_group(g)
            if group_data and 'name' in group_data:
                group_names.append(group_data['name'])

        if group_names:
            union_display = f"🧩 {union_name} | Группы: {', '.join(group_names)}"
        else:
            union_display = f"🧩 {union_name}"

        buttons.append(telebot.types.KeyboardButton(union_display))

    keyboard.add(*buttons, telebot.types.KeyboardButton("❌ Отмена"))
    return keyboard

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
            button_text = '🔢 Сменить на: Знаменатель'
            button_callback = f"group_{group_id}_week_denominator"
        else:
            button_text = '🔢 Сменить на: Числитель'
            button_callback = f"group_{group_id}_week_numerator"
    elif isNumerator == 1:
        button_text = '🔢 Сменить на: Числитель'
        button_callback = f"group_{group_id}_week_denominator"
    elif isNumerator == 0:
        button_text = '🔢 Сменить на: Знаменатель'
        button_callback = f"group_{group_id}_week_numerator"
    button = telebot.types.InlineKeyboardButton(
        text=button_text,
        callback_data=button_callback
    )
    keyboard_numerator.add(button)
    return keyboard_numerator

def get_keyboard_toggle_week(week_type):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if week_type == -1:
        if is_numerator():
            button_text = "🔢 Сменить на: Знаменатель"
            new_type = 1
        else:
            button_text = "🔢 Сменить на: Числитель"
            new_type = 0
    elif week_type == 0:
        button_text = "🔢 Сменить на: Знаменатель"
        new_type = 1
    else:
        button_text = "🔢 Сменить на: Числитель"
        new_type = 0
    keyboard.add(telebot.types.InlineKeyboardButton(button_text, callback_data=f"toggle_week_{new_type}"))
    return keyboard

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