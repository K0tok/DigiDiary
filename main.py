import telebot
import config
from DataBase import *
from Functions import *
from keyboards import *
from datetime import datetime, timedelta 
from threading import Thread
from time import sleep

bot = telebot.TeleBot(config.TG_API_TOKEN, parse_mode='HTML')
url = config.URL
@bot.message_handler(commands=["admin_test"])
def test(message): 
        print(bot.get_chat(message.chat.id))


@bot.message_handler(commands=["start"])
def send_welcome(message): 
    user_id = message.from_user.id
    if user_id not in select_users_tgId():
        # bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)
        user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        bot.send_message(message.chat.id, f"Пользователь {user_name} зарегистрирован успешно. Добро пожаловать в ЭДС!", reply_markup=keyboard_commands if message.chat.id > 0 else keyboard_commands_chat)
        add_user(user_id, user_name)
    if message.chat.id > 0:
        bot.send_message(
            message.chat.id, 
            f'''<b>👋 Добро пожаловать в DigiDiary</b>

📌 Здесь вы можете:
- Просматривать домашние задания
- Смотреть расписание занятий
- Получать напоминания о дедлайнах

Выберите нужную функцию:''', 
            reply_markup=keyboard_commands)
    else:
        bot.send_message(
            message.chat.id, 
            f'''<b>👋 Добро пожаловать в DigiDiary</b>

📌 Здесь вы можете:
- Добавлять домашние задания
- Управлять учебной группой

Выберите нужную функцию:''', 
            reply_markup=keyboard_commands_chat)


@bot.message_handler(commands=["schedule"])
def send_schedule_simple(message):
        # Разбираем текст сообщения      
        command, *args = message.text.split()
        if len(args) < 1:
            bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=create_keyboard_groups('week', message.chat.id))
            return
        else: 
            group_name = args[0].upper()  # Название группы
            today_only = False
            
            # Проверяем, запрошено ли расписание только на сегодня
            if len(args) > 1 and args[1].lower() == "today":
                today_only = True
            
            group_id = select_group_by_name(group_name)['id']
            # Получаем расписание
            schedule_text = get_schedule(url, group_id, -1, today_only)
            
            # Отправляем расписание пользователю
            bot.reply_to(message, schedule_text)

def send_my_schedule(message, week_type=-1, today_only=False):
    user_tgId = message.chat.id
    if message.chat.id > 0:  # Только в ЛС
        user_data = select_user(user_tgId)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Вы не зарегистрированы.", reply_markup=keyboard_commands)
            return

        user_id = user_data['id']
        user_unions = select_user_unions(user_id)

        if not user_unions:
            bot.send_message(message.chat.id, "📭 Вы не состоите ни в одном объединении.", reply_markup=keyboard_commands)
            return

        all_schedules = []
        days_of_week = ["ПОНЕДЕЛЬНИК", "ВТОРНИК", "СРЕДА", "ЧЕТВЕРГ", "ПЯТНИЦА", "СУББОТА", "ВОСКРЕСЕНЬЕ"]
        current_day = days_of_week[datetime.now().weekday()]

        for u in user_unions:
            union_groups = select_union_groups(u['union_id'])
            for g in union_groups:
                group_name = select_group(g)['name']

                try:
                    schedule_data = get_schedule(url, g, week_type, today_only=today_only)  # Получаем расписание
                    if schedule_data.startswith("Ошибка") or schedule_data.startswith("Группа"):
                        continue

                    lines = schedule_data.split('\n')
                    filtered_lines = [line for line in lines]
                    # all_schedules.append(f"<b>📘 Группа:</b> {group_name}")
                    all_schedules.extend(filtered_lines)

                except Exception as e:
                    print(f"Ошибка при получении расписания для группы {group_name}: {e}")

        if not all_schedules:
            bot.send_message(message.chat.id, "❌ Расписание не найдено для ваших групп.")
            return

        result_text = "\n".join(all_schedules)
        bot.send_message(message.chat.id, result_text, reply_markup=get_keyboard_toggle_week(week_type) if not today_only else keyboard_commands)
    else:
        bot.send_message(message.chat.id, "❌ Эта функция доступна только в личных сообщениях.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_week_"))
def handle_toggle_week(call):
    week_type = int(call.data.split("_")[2])
    try:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass

    send_my_schedule(call.message, week_type=week_type)


@bot.message_handler(commands=["profile"])
def profile_message(message):
    bot.delete_message(message.chat.id, message.message_id)
    if message.chat.id < 0:
        bot.send_message(message.chat.id, create_profile_message(message.chat.id), reply_markup=keyboard_profile_chat)
    else:
        bot.send_message(message.chat.id, create_profile_message(message.chat.id), reply_markup=keyboard_profile)

@bot.message_handler(commands=["union"])
def union_message(message):
    if message.chat.id < 0:
        if message.chat.id not in select_unions_tgId():
            try:
                user_id = message.from_user.id
                # Регистрация пользователя, который пригласил бота в чат, если не зарегистрирован 
                if user_id not in select_users_tgId():
                    user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
                    add_user(user_id, user_name)

                union_tgId = message.chat.id
                union_name = bot.get_chat(message.chat.id).title
                union_created_by_id = select_user(message.from_user.id)['id']

                if create_union(union_tgId, union_name, union_created_by_id):
                    add_user_to_union(select_user(user_id)['id'], select_union(message.chat.id)['id'])
                    bot.send_message(message.chat.id, "Чат успешно зарегистрирован. Теперь выберите к каким группам присоединить чат:", reply_markup=create_keyboard_groups(None, message.chat.id))
            except Exception as e:
                bot.send_message(message.chat.id, "Возникла ошибка при регистрации группы.")
                print(e)
        else:
            bot.send_message(message.chat.id, "Ваша группа зарегистрирована! Выберите к каким группам присоединить чат или открепить:", reply_markup=create_keyboard_groups(None, message.chat.id, True))
    else:
        bot.send_message(message.chat.id, "Эта функция доступна только в групповом чате.")

@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    if message.new_chat_members[0].id != 7000728406:
        user_name = message.new_chat_members[0].first_name 
        user_id = message.new_chat_members[0].id

        if user_id not in select_users_tgId():
            user_name = create_user_name(message.new_chat_members[0].first_name, message.new_chat_members[0].last_name, message.new_chat_members[0].username)
            add_user(user_id, user_name)
        union_users = []
        for um in select_union_users(select_union(message.chat.id)['id']):
            union_users.append(um['user_id'])
        if select_user(user_id)['id'] in union_users:
            if add_user_to_union(select_user(user_id)['id'], select_union(message.chat.id)['id']):
                bot.send_message(message.chat.id, "Добро пожаловать, {0}!".format(user_name))
            else:
                bot.send_message(message.chat.id, "Не удалось прикрепить пользователя {0}.".format(user_name))

    else:
        union_message(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("groupId_"))
def create_unionMember(call):
    group_id = call.data.split("_")[1]
    isAdd = True if call.data.split("_")[2] == 'add' else False
    isDelete = True if call.data.split("_")[2] == 'delete' else False

    if isAdd:
        add_union_to_group(select_union(call.message.chat.id)['id'], group_id)
        bot.send_message(call.message.chat.id, f"Теперь ваш чат закреплен за группой {select_group(group_id)['name']}")
    elif isDelete:
        delete_union_from_group(select_union(call.message.chat.id)['id'], group_id)
        bot.send_message(call.message.chat.id, f"Ваш чат откреплен от группы {select_group(group_id)['name']}")

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def send_schedule(call):
    group_id = call.data.split("_")[1]
    today_only = True if call.data.split("_")[2] == "today" else False
    if call.data.split("_")[3] == "numerator":
        is_numerator = 0
    elif call.data.split("_")[3] == "denominator":
        is_numerator = 1
    else:
        is_numerator = -1

    schedule_text = get_schedule(url, group_id, is_numerator, today_only)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if is_numerator == -1:
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    bot.send_message(call.message.chat.id, schedule_text, reply_markup=keyboard_numerator(is_numerator, group_id))
    
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("changeMyName_"))
def changeMyName(call):
    isUnion = True if call.data.split("_")[1] == "union" else False
    if not isUnion:
        msg = bot.send_message(call.message.chat.id, "✏️ Изменение имени\nВведите новое:")
    else:
        msg = bot.send_message(call.message.chat.id, "✏️ Изменение названия\nВведите новое:")
    bot.register_next_step_handler(msg, lambda m: changeMyName_secondStep(m, isUnion))
    bot.answer_callback_query(call.id)

def changeMyName_secondStep(message, isUnion = False):
    newName = message.text
    if not isUnion:
        update_user(message.chat.id, newName)
        bot.send_message(message.chat.id, f"Ваше имя изменено на <i>{newName}</i>")
    else:
        update_union(message.chat.id, newName)
        bot.set_chat_title(message.chat.id, title=newName)
        bot.send_message(message.chat.id, f"Имя объединения изменено на <i>{newName}</i>")


def new_homework(message):
    if message.chat.id > 0:
        bot.reply_to(message, "Эта функция доступна только в групповом чате объединения.")
    else:
        user_tgId = message.from_user.id
        if user_tgId not in select_users_tgId():
            bot.reply_to(message, "Вы не зарегистрированы в системе. Пожалуйста зарегистрируйтесь")
            return

        # Получаем данные о чате-объединении
        union_data = select_union(message.chat.id)
        if not union_data:
            bot.reply_to(message, "❌ Этот чат не зарегистрирован как объединение.")
            return

        union_id = union_data['id']

        # Проверяем, состоит ли пользователь в объединении
        if select_user(user_tgId)['id'] not in [ u['user_id'] for u in select_union_users(union_id) ]:
            bot.reply_to(
                message,
                "❌ Вы не состоите в этом объединении. Нажмите кнопку <i>➕ Прикрепить меня</i>, чтобы получить доступ.",
                reply_markup=telebot.types.ReplyKeyboardMarkup(resize_keyboard=True).add(telebot.types.KeyboardButton("➕ Прикрепить меня"))
            )
            return

        groupNames = [select_group(g)['name'] for g in select_union_groups(union_id)]

        # Клавиатура с предметами и отменой
        keyboard = create_keyboard_subjects(url, groupNames)
        keyboard.add(telebot.types.KeyboardButton("❌ Отмена"))

        msg = bot.send_message(
            message.chat.id,
            "📌 Добавление нового задания\n\nВыберите предмет из списка или введите вручную.\n\n├ -\n├ Сдать до: -\n└ Описание: -",
            reply_markup=keyboard
        )
        bot.register_next_step_handler(msg, lambda m: new_homework_secondStep(m, homework(select_user(user_tgId)['id'])))

def new_homework_secondStep(message, homework_obj):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "❌ Добавление домашнего задания отменено.", reply_markup=keyboard_commands_chat)
        return
    msg = bot.send_message(
            message.chat.id,
            f'📌 Добавление нового задания\n\nВведите срок сдачи\n<i>Пример: 2025-05-19</i>\n\n├ {message.text}\n├ Сдать до: -\n└ Описание: -',
            reply_markup=keyboard_cancel
        )
    bot.register_next_step_handler(msg, lambda m: new_homework_thirdStep(m, homework(homework_obj["user_id"], message.text)))
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)

def new_homework_thirdStep(message, homework_obj):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "❌ Добавление домашнего задания отменено.", reply_markup=keyboard_commands_chat)
        return
    
    is_valid, result = is_valid_date(message.text)
    if not is_valid:
        bot.send_message(message.chat.id, f"❌ {result}")
        msg = bot.send_message(
            message.chat.id, 
            f'📌 Добавление нового задания\n\nВведите срок сдачи\n<i>Пример: 2025-05-19</i>\n\n├ {homework_obj["subject"]}\n├ Сдать до: -\n└ Описание: -',
            reply_markup=keyboard_cancel
            )
        bot.register_next_step_handler(msg, lambda m: new_homework_thirdStep(m, homework_obj))
        return
    
    msg = bot.send_message(
        message.chat.id, 
        f'📌 Добавление нового задания\n\nВведите задание:\n\n├ {homework_obj["subject"]}\n├ Сдать до: {result}\n└ Описание: -',
        reply_markup=keyboard_cancel
        )
    bot.register_next_step_handler(msg, lambda m: new_homework_fourthStep(m, homework(homework_obj["user_id"], homework_obj["subject"], result)))
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)

def new_homework_fourthStep(message, homework_obj):
    if message.text == "❌ Отмена":
        bot.send_message(message.chat.id, "❌ Добавление домашнего задания отменено.", reply_markup=keyboard_commands_chat)
        return
    homework_id = create_homework(homework_obj["user_id"], homework_obj["subject"], homework_obj["due_date"], message.text, select_union(message.chat.id)['id'])
    done_homework = select_homework(homework_id)
    bot.send_message(
        message.chat.id, 
        f'📌 Задание добавлено\n├ {done_homework["subject"]}\n├ Сдать до: {done_homework["due_date"].strftime("%d.%m.%Y")}\n└ Описание: {done_homework["description"]}', 
        reply_markup=keyboard_commands_chat
        )
    bot.delete_message(message.chat.id, message.message_id)
    bot.delete_message(message.chat.id, message.message_id - 1)

def view_homework_menu(message):
    user_tgId = message.from_user.id
    if message.chat.id > 0:  # Только в ЛС
        user_data = select_user(user_tgId)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Вы не зарегистрированы.", reply_markup=keyboard_commands)
            return
        user_id = user_data['id']
        user_unions = select_user_unions(user_id)

        if not user_unions:
            bot.send_message(message.chat.id, "📭 У вас нет объединений.", reply_markup=keyboard_commands)
            return

        group_names = set()
        for u in user_unions:
            union_groups = select_union_groups(u['union_id'])
            for g in union_groups:
                group_names.add(select_group(g)['name'])

        if not group_names:
            bot.send_message(message.chat.id, "📭 Нет групп для просмотра.", reply_markup=keyboard_commands)
            return

        msg = bot.send_message(message.chat.id, "Выберите группу для просмотра ДЗ:", reply_markup=get_homework_keyboard(user_id))
        bot.register_next_step_handler(msg, show_homework_by_group_or_all)
    else:
        bot.send_message(message.chat.id, "❌ Эта функция доступна только в личных сообщениях.", reply_markup=keyboard_commands_chat)


def show_homework_by_group_or_all(message):
    selected = message.text.strip()
    if selected == "❌ Отмена":
        send_welcome(message)
        return
    user_tgId = message.from_user.id
    user_data = select_user(user_tgId)

    if not user_data:
        bot.send_message(message.chat.id, "❌ Вы не зарегистрированы.", reply_markup=keyboard_commands)
        return

    user_id = user_data['id']
    homeworks = select_homeworks_by_user(user_id, is_archived=False)

    if not homeworks:
        bot.send_message(message.chat.id, "📭 У вас пока нет домашних заданий.", reply_markup=get_archive_keyboard())
        return

    bot.send_message(message.chat.id, f"📘 Задания ({selected}):", reply_markup=keyboard_commands)

    if selected == "📚 Все задания":
        # Группируем задания по объединениям
        homework_by_union = {}
        for hw in homeworks:
            unions = get_homework_unions(hw["id"])
            for union in unions:
                union_name = union["name"]
                group_names = get_union_group_names(union["id"])

                key = (union_name, tuple(group_names))
                if key not in homework_by_union:
                    homework_by_union[key] = []
                homework_by_union[key].append(hw)

        if homework_by_union:
            for (union_name, group_names), hw_list in homework_by_union.items():
                groups_str = ", ".join(group_names)
                bot.send_message(message.chat.id, f"<b>🧩 Объединение:</b> {union_name}\n<b>📁 Группы:</b> {groups_str}", reply_markup=keyboard_commands)
                
                for hw in hw_list:
                    is_done = get_homework_status(hw['id'], user_id)
                    status_text = "✅ Выполнено" if is_done else "❌ Не выполнено"
                    text = f'''📌 <b>{hw["subject"]}</b>
📅 Сдать до: {hw["due_date"].strftime("%d.%m.%Y")}
📝 Описание: {hw["description"]}
📊 Статус: {status_text}'''
                    bot.send_message(message.chat.id, text, reply_markup=create_keyboard_isDone(hw, is_done))
        else:
            bot.send_message(message.chat.id, "❌ Нет заданий для отображения.", reply_markup=keyboard_commands)

    elif selected.startswith("🧩"):
        # Извлекаем название объединения из кнопки
        union_name = selected.split("|")[0].replace("🧩", "").strip()

        # Находим объединение по имени
        union_data = select_union_by_name(union_name)
        if not union_data:
            bot.send_message(message.chat.id, "❌ Объединение не найдено.", reply_markup=keyboard_commands)
            return

        union_id = union_data['id']

        # Получаем все задания этого объединения
        homeworks = select_homeworks_by_union(union_id, user_id, is_archived=False)

        if not homeworks:
            bot.send_message(message.chat.id, "📭 Нет активных заданий для этого объединения.", reply_markup=keyboard_commands)
            return

        for hw in homeworks:
            is_done = get_homework_status(hw['id'], user_id)
            status_text = "✅ Выполнено" if is_done else "❌ Не выполнено"
            text = f'''📌 <b>{hw["subject"]}</b>
    📅 Сдать до: {hw["due_date"].strftime("%d.%m.%Y")}
    📝 Описание: {hw["description"]}
    📊 Статус: {status_text}'''
            bot.send_message(message.chat.id, text, reply_markup=create_keyboard_isDone(hw, is_done))

    bot.send_message(message.chat.id, f"🗂 Просмотреть задания в архиве", reply_markup=get_archive_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_hw_"))
def toggle_homework_status(call):
    homework_id = int(call.data.split("_")[2])
    user_tgId = call.from_user.id
    user_data = select_user(user_tgId)

    if not user_data:
        bot.answer_callback_query(call.id, "❌ Вы не зарегистрированы.")
        return

    user_id = user_data['id']
    is_done = not get_homework_status(homework_id, user_id)
    success = set_homework_status(homework_id, user_id, is_done)

    if not success:
        bot.answer_callback_query(call.id, "❌ Ошибка сохранения")
        return

    # Получаем оригинальное сообщение
    done_homework = select_homework(homework_id)
    if not done_homework:
        bot.answer_callback_query(call.id, "❌ Задание не найдено")
        return

    # Получаем новый статус
    status_text = "✅ Выполнено" if is_done else "❌ Не выполнено"
    status_button_text = "❌ Отменить выполнение" if is_done else "✅ Выполнить"

    # Формируем текст сообщения
    updated_text = f'''📌 <b>{done_homework["subject"]}</b>
📅 Сдать до: {done_homework["due_date"].strftime("%d.%m.%Y")}
📝 Описание: {done_homework["description"]}
📊 Статус: {status_text}'''


    # Редактируем сообщение
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=updated_text,
        reply_markup=create_keyboard_isDone(done_homework, is_done)
    )

    bot.answer_callback_query(call.id, "Статус изменён")

@bot.callback_query_handler(func=lambda call: call.data.startswith("archive_hw_"))
def handle_archive_homework(call):
    homework_id = int(call.data.split("_")[2])
    user_tgId = call.from_user.id
    user_data = select_user(user_tgId)

    if not user_data:
        bot.answer_callback_query(call.id, "❌ Вы не зарегистрированы.")
        return

    user_id = user_data['id']
    success = archive_homework(homework_id, user_id, is_archived=True)

    if not success:
        bot.answer_callback_query(call.id, "❌ Не удалось архивировать задание.")
        return

    # Редактируем сообщение — убираем его
    bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=None
    )

    bot.answer_callback_query(call.id, "Задание отправлено в архив")

@bot.callback_query_handler(func=lambda call: call.data == "archive_menu")
def show_archive_menu(call):
    message = call.message
    bot.delete_message(message.chat.id, message.message_id)
    user_tgId = message.chat.id
    bot.answer_callback_query(call.id)
    if message.chat.id > 0:  # Только в ЛС
        user_data = select_user(user_tgId)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Вы не зарегистрированы.", reply_markup=keyboard_commands)
            return

        user_id = user_data['id']
        homeworks = select_homeworks_by_user(user_id, is_archived=True)

        if not homeworks:
            bot.send_message(message.chat.id, "📭 Ваш архив пуст.", reply_markup=keyboard_commands)
            return

        bot.send_message(message.chat.id, "<b>🗂 Архив заданий:</b>", reply_markup=keyboard_commands)
        for hw in homeworks:
            text = f'''📌 <b>{hw["subject"]}</b>
📅 Сдать до: {hw["due_date"].strftime("%d.%m.%Y")}
📝 Описание: {hw["description"]}'''
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton("↩️ Вернуть из архива", callback_data=f"unarchive_hw_{hw['id']}"))
            bot.send_message(message.chat.id, text, reply_markup=keyboard)
            bot.answer_callback_query(call.id)
    else:
        bot.send_message(message.chat.id, "❌ Эта функция доступна только в личных сообщениях.", reply_markup=keyboard_commands)

@bot.callback_query_handler(func=lambda call: call.data.startswith("unarchive_hw_"))
def handle_unarchive_homework(call):
    homework_id = int(call.data.split("_")[2])
    user_tgId = call.from_user.id
    user_data = select_user(user_tgId)

    if not user_data:
        bot.answer_callback_query(call.id, "❌ Вы не зарегистрированы.")
        return

    user_id = user_data['id']
    success = archive_homework(homework_id, user_id, is_archived=False)

    if not success:
        bot.answer_callback_query(call.id, "❌ Не удалось восстановить задание.")
        return

    done_homework = select_homework(homework_id)
    updated_text = f'''📌 <b>{done_homework["subject"]}</b>
📅 Сдать до: {done_homework["due_date"].strftime("%d.%m.%Y")}
📝 Описание: {done_homework["description"]}'''

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=updated_text,
        reply_markup=None
    )
    bot.answer_callback_query(call.id, "🔄 Задание возвращено из архива")


@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(message):
    user = message.left_chat_member
    
    # Проверяем, есть ли такое объединение
    union_data = select_union(message.chat.id)
    if not union_data:
        return

    union_id = union_data['id']
    success = remove_user_from_union(select_user(user.id)['id'], union_id)

    if success:
        try:
            bot.send_message(user.id, f"❌ Вы были удалены из объединения <b>{union_data['name']}</b>.")
        except Exception as e:
            print("Не удалось отправить ЛС пользователю:", e)        
        try:
            bot.send_message(message.chat.id, f"❌ Пользователь {select_user(user.id)['name']} был удален из объединения.")
        except Exception as e:
            print("Не удалось отправить уведомление об исключении:", e)


def check_deadlines():
    users = select_users_tgId() 
    now = datetime.now().date()

    for tgId in users:
        user_data = select_user(tgId)
        if not user_data:
            continue

        user_id = user_data['id']

        # Получаем только невыполненные и неархивированные задания
        homeworks = select_homeworks_by_user(user_id, is_archived=False)

        deadlines_urgent = []
        deadlines_soon = []

        for hw in homeworks:
            is_done = get_homework_status(hw['id'], user_id)
            if is_done:
                continue  # Пропускаем выполненные

            due_date = hw["due_date"].date()
            delta = (due_date - now).days

            if 0 < delta <= 1:
                deadlines_urgent.append(hw)
            elif 1 < delta <= 3:
                deadlines_soon.append(hw)

        try:
            if deadlines_urgent:
                bot.send_message(
                    tgId,
                    "<b>⚠️ Срочные задания:</b>\n"
                    + "\n".join([f"📌 {hw['subject']} — сдать до {hw['due_date'].date()}" for hw in deadlines_urgent])
                )
            if deadlines_soon:
                bot.send_message(
                    tgId,
                    "<b>⏳ Задания на ближайшие дни:</b>\n"
                    + "\n".join([f"📌 {hw['subject']} — сдать до {hw['due_date'].date()}" for hw in deadlines_soon])
                )
        except Exception as e:
            print(f"[Напоминание] Не удалось отправить сообщение пользователю {tgId}: {e}")

def run_reminder():
    while True:
        try:
            check_deadlines()
        except Exception as e:
            print("Ошибка при выполнении напоминаний:", e)
        sleep(86400)  # 24 часа между проверками

Thread(target=run_reminder, daemon=True).start()

@bot.message_handler(commands=["remind_me"])
def remind_me(message):
    if message.chat.id > 0:
        user_id = message.from_user.id
        user_data = select_user(user_id)
        if not user_data:
            bot.send_message(message.chat.id, "❌ Вы не зарегистрированы.")
            return
        homeworks = select_homeworks_by_user(user_data['id'])
        now = datetime.now().date()
        urgent = [h for h in homeworks if (h["due_date"].date() - now).days <= 3]
        if urgent:
            bot.send_message(message.chat.id, "<b>📌 Скорые дедлайны:</b>\n" + "\n".join([f"📌 {h['subject']} — {h['due_date'].date()}" for h in urgent]))
        else:
            bot.send_message(message.chat.id, "📭 У вас нет скорых дедлайнов.")
    else:
        bot.send_message(message.chat.id, "❌ Эта команда доступна только в личных сообщениях.")


@bot.message_handler(commands=["help"])
def send_help(message):
    if message.chat.id > 0:
        bot.send_message(
            message.chat.id,
            '''<b>📘 Справка: основные команды</b>

<b>🗓️ Моё расписание</b> — показать всё расписание на неделю  
<b>📅 Расписание на сегодня</b> — показать расписание только на сегодня  
<b>📚 Расписание занятий НТИ</b> — получить расписание для любой группы  
<b>📒 Посмотреть мои ДЗ</b> — просмотр домашних заданий  
<b>👤 Мой профиль</b> — информация о себе, можно изменить имя  

<i>Вы также можете использовать эти команды:</i>
/start — начать работу с ботом''',
            parse_mode='HTML',
            reply_markup=keyboard_commands
        )
    else:
        bot.send_message(
            message.chat.id,
            '''<b>📘 Справка: команды в чате</b>

<b>📚 Расписание занятий НТИ</b> — получить расписание любой группы НТИ  
<b>📌 Добавить новое задание</b> — создать ДЗ для студентов  
<b>⚙️ Параметры</b> — регистрация чата как объединения и связь с группами  
<b>➕ Прикрепить меня</b> — чтобы получать задания в ЛС  
<b>👤 Профиль группы</b> — информация о текущем объединении

<i>Команды:</i>
/schedule [Группа] — расписание на неделю  
/schedule [Группа] today — расписание на сегодня  
/help — эта справка  
/about — информация об авторе''',
            parse_mode='HTML',
            reply_markup=keyboard_commands_chat
        )


@bot.message_handler(commands=["about"])
def send_about(message):
    bot.send_message(message.chat.id, "Создатель бота: @K0tok")


@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message):
    if message.text in ["📚 Расписание занятий НТИ", "Расписание занятий НТИ", "📚"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=create_keyboard_groups('week', message.chat.id ))
    if message.text in ["🗓️ Моё расписание", "Моё расписание", "🗓️"]:
        send_my_schedule(message, today_only=False)
    if message.text in ["📅 Расписание на сегодня", "Расписание на сегодня", "📅"]:
        send_my_schedule(message, today_only=True)
    if message.text in ["➕ Прикрепить меня", "Прикрепить меня", "➕"]:
        union_id = message.chat.id
        if union_id > 0:
            bot.send_message(message.chat.id, f"Эта команда только для чата групп.")
        else:
            user_id = message.from_user.id
            union_users = []
            for um in select_union_users(select_union(union_id)['id']):
                union_users.append(um['user_id'])
            if select_user(user_id)['id'] in union_users:
                bot.send_message(message.chat.id, f"Вы уже прикреплены!", reply_markup=keyboard_commands_chat)
            else:
                if user_id not in select_users_tgId():
                    user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
                    add_user(user_id, user_name)
                    add_user_to_union(select_user(user_id)['id'], select_union(union_id)['id'])
                    bot.send_message(message.chat.id, f"Пользователь {user_name} зарегистрирован и прикреплён успешно. Добро пожаловать в ЭДС!", reply_markup=keyboard_commands_chat)
                else:
                    add_user_to_union(select_user(user_id)['id'], select_union(union_id)['id'])
                    bot.send_message(message.chat.id, f"Пользователь {select_user(message.from_user.id)['name']} прикреплен успешно!", reply_markup=keyboard_commands_chat)
    if message.text in ["⚙️ Параметры", "Параметры", "⚙️"]:
        union_message(message)
    if message.text in ["👤 Мой профиль", "👤 Профиль группы", "Мой профиль", "Профиль группы", "👤"]:
        profile_message(message)
    if message.text in ["📒 Посмотреть мои ДЗ", "Посмотреть мои ДЗ", "📒"]:
        view_homework_menu(message)
    if message.text in ["📌 Добавить новое задание", "Добавить новое задание", "📌"]:
        new_homework(message)

bot.infinity_polling()
