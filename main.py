import telebot
import config
from DataBase import *
from Functions import *
from keyboards import *

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
    else:
        if message.chat.id > 0:
            bot.send_message(message.chat.id, f"Рады видеть вас снова, {message.from_user.first_name}!", reply_markup=keyboard_commands)
        else:
            bot.send_message(message.chat.id, f"Выберите команду!", reply_markup=keyboard_commands_chat)


@bot.message_handler(commands=["schedule"])
def send_schedule_simple(message):
        # Разбираем текст сообщения             ДОБАВИТЬ РАЗДЕЛЕНИЕ НА ЛИЧКУ И ЧАТ
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
                union_tgId = message.chat.id
                union_name = bot.get_chat(message.chat.id).title
                union_created_by_id = select_user(message.from_user.id)['id']
                user_id = message.from_user.id

                # Регистрация пользователя, который пригласил бота в чат, если не зарегистрирован 
                if user_id not in select_users_tgId():
                    user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)

                    add_user(user_id, user_name)

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
        bot.send_message(message.chat.id, "Добро пожаловать, {0}!".format(user_name))

        if user_id not in select_users_tgId():
            user_name = create_user_name(message.new_chat_members[0].first_name, message.new_chat_members[0].last_name, message.new_chat_members[0].username)
            add_user(user_id, user_name)

        add_user_to_union(select_user(user_id)['id'], select_union(message.chat.id)['id'])
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
    bot.register_next_step_handler(msg, changeMyName_secondStep(call.message, call.message.text, isUnion))

def changeMyName_secondStep(message, newName, isUnion = False):
    if not isUnion:
        update_user(message.chat.id, newName)
        bot.send_message(message.chat.id, f"Ваше имя изменено на <i>{newName}</i>")
    else:
        update_union(message.chat.id, newName)
        bot.set_chat_title(message.chat.id, title=newName)
        bot.send_message(message.chat.id, f"Имя объединения изменено на <i>{newName}</i>")


@bot.message_handler(content_types=['new_chat_title'])
def new_chat_title(message):
    changeMyName_secondStep(message, bot.get_chat(message.chat.id).title, True)


def new_homework(message):
    if message.chat.id > 0:
        bot.reply_to(message, "Эта функция доступна только в групповом чате объединения.")
    else:
        user_tgId = message.from_user.id
        if user_tgId not in select_users_tgId():
            bot.reply_to(message, "Вы не зарегистрированы в системе. Пожалуйста зарегистрируйтесь")
        elif select_user(user_tgId)['id'] not in select_union_users(message.chat.id):
            bot.reply_to(message, "Вы не прикреплены к объединению. Пожалуйста нажмите кнопку <i>➕ Прикрепить меня</i>")
        else:
            union_id = select_union(message.chat.id)['id']
            groupNames = []
            for g in select_union_groups(union_id):
                groupNames.append(select_group(g)['name'])
            msg = bot.send_message(message.chat.id, "📌 Добавление нового задания\nВыберите предмет из списка или введите вручную.", reply_markup=create_keyboard_subjects(url, groupNames))
            bot.register_next_step_handler(msg, new_homework_secondStep(message, homework(select_user()['id'])))

def new_homework_secondStep(message, homework_obj):
    msg = bot.send_message(message.chat.id, "📌 Добавление нового задания\nВведите срок сдачи\n<i>Пример: 2025-05-19</i>", )
    bot.register_next_step_handler(msg, new_homework_thirdStep(message, homework(homework_obj["user_id"], message.text)))

def new_homework_thirdStep(message, homework_obj):
    msg = bot.send_message(message.chat.id, "📌 Добавление нового задания\nВведите задание:", )
    bot.register_next_step_handler(msg, new_homework_fourthStep(message, homework(homework_obj["user_id"], homework_obj["subject"], message.text)))

def new_homework_fourthStep(message, homework_obj):
    homework_id = create_homework(homework_obj["user_id"], homework_obj["subject"], homework_obj["due_date"], message.text)
    done_homework = select_homework(homework_id)
    bot.send_message(message.chat.id, f'📌 Добавление нового задания\n├ {done_homework["subject"]}\n├ Сдать до: {done_homework["due_date"]}\n└ Описание: {done_homework["description"]}')

@bot.message_handler(commands=["help"])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Список команд данного бота:\n\nstart - Начало работы\nhelp - Справка по командам бота и работе с ним\nabout - Информация об авторе",
        reply_markup=keyboard_commands,
    )


@bot.message_handler(commands=["about"])
def send_about(message):
    bot.send_message(message.chat.id, "Создатель бота: @K0tok")


@bot.message_handler(func=lambda message: True)
def echo_all(message: telebot.types.Message):
    if message.text in ["📚 Расписание занятий НТИ", "Расписание занятий НТИ", "📚"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=create_keyboard_groups('week', message.chat.id ))
        return
    if message.text in ["🗓️ Моё расписание", "Моё расписание", "🗓️"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=create_keyboard_groups('week', message.chat.id ))
        return
    if message.text in ["📅 Расписание на сегодня", "Расписание на сегодня", "📅"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=create_keyboard_groups('today', message.chat.id ))
        return
    if message.text in ["➕ Прикрепить меня", "Прикрепить меня", "➕"]:
        union_id = message.chat.id
        if union_id > 0:
            bot.send_message(message.chat.id, f"Эта команда только для чата групп.")
        else:
            user_id = message.from_user.id
            if user_id not in select_union_users(union_id):
                bot.send_message(message.chat.id, f"Вы уже прикреплены!", reply_markup=keyboard_commands_chat)
            else:
                if user_id not in select_users_tgId():
                    user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
                    add_user(user_id, user_name)
                    add_user_to_union(select_user(user_id)['id'], select_union(union_id)['id'])
                    bot.send_message(message.chat.id, f"Пользователь {user_name} зарегистрирован и прикреплён успешно. Добро пожаловать в ЭДС!", reply_markup=keyboard_commands_chat)
                else:
                    add_user_to_union(select_user(user_id)['id'], select_union(union_id)['id'])
                    bot.send_message(message.chat.id, f"Пользователь {user_name} прикреплен успешно!", reply_markup=keyboard_commands_chat)
    if message.text in ["⚙️ Параметры", "Параметры", "⚙️"]:
        union_message(message)
    if message.text in ["👤 Мой профиль", "👤 Профиль группы", "Мой профиль", "Профиль группы", "👤"]:
        profile_message(message)
    if message.text in ["📖 Дневник", "Дневник", "📖"]:
        bot.reply_to(message, "📖 Дневник\nВыберите функцию:", reply_markup=keyboard_diary_functions)
    # if message.text in ["📒 Посмотреть мои ДЗ", "Посмотреть мои ДЗ", "📒"]:
        # 
    if message.text in ["📌 Добавить новое задание", "Добавить новое задание", "📌"]:
        new_homework(message)

bot.infinity_polling()
