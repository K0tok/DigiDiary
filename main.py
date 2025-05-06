import telebot
import config
from DataBase import *
from Functions import *
from keyboards import *

bot = telebot.TeleBot(config.TG_API_TOKEN, parse_mode='HTML')
url = config.URL
# @bot.message_handler(commands=["admin_test"])
# def test(message): 
#         bot.send_message(message.chat.id, f"\{message.chat.id}")


@bot.message_handler(commands=["start"])
def send_welcome(message): 
    user_id = message.from_user.id
    if user_id not in select_users_tgId():
        # bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)
        user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)
        bot.send_message(message.chat.id, f"Пользователь {user_name} зарегистрирован успешно. Добро пожаловать в ЭДС!", reply_markup=keyboard_commands)
        add_user(user_id, user_name)
    else:
        if message.chat.id > 0:
            bot.send_message(message.chat.id, f"Рады видеть вас снова, {message.from_user.first_name}!", reply_markup=keyboard_commands)
        else:
            bot.send_message(message.chat.id, f"Выберите комманду!", reply_markup=keyboard_commands)


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

@bot.message_handler(commands=["union"])
def create_union_message(message):
    if message.chat.id < 0:
        if message.chat.id not in select_unions_tgId():
            try:
                union_tgId = message.chat.id
                union_name = bot.get_chat(message.chat.id).title
                union_created_by_id = message.from_user.id
                user_id = message.from_user.id

                # Регистрация пользователя, который пригласил бота в чат, если не зарегистрирован 
                if user_id not in select_users_tgId():
                    user_name = create_user_name(message.from_user.first_name, message.from_user.last_name, message.from_user.username)

                    add_user(user_id, user_name)

                if create_union(union_tgId, union_name, union_created_by_id):
                    add_user_to_union(user_id, message.chat.id)
                    bot.send_message(message.chat.id, "Чат успешно зарегистрирован. Теперь выберите к каким группам присоединить чат:", reply_markup=create_keyboard_groups(None, message.chat.id))
            except Exception as e:
                bot.send_message(message.chat.id, "Возникла ошибка при регистрации группы.")
                print(e)
        else:
            bot.send_message(message.chat.id, "Ваша группа зарегистрирована! Выберите к каким группам присоединить чат или открепить:", reply_markup=create_keyboard_groups(None, message.chat.id))
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

        add_user_to_union(user_id, message.chat.id)
    else:
        create_union_message(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("groupId_"))
def create_unionMember(call):
    group_id = call.data.split("_")[1]
    isAdd = True if call.data.split("_")[2] == 'add' else False
    isDelete = True if call.data.split("_")[2] == 'delete' else False

    if isAdd:
        add_union_to_group(call.message.chat.id, group_id)
        bot.send_message(call.message.chat.id, f"Теперь ваш чат закреплен за группой {select_group(group_id)['name']}")
    elif isDelete:
        delete_union_from_group(call.message.chat.id, group_id)
        bot.send_message(call.message.chat.id, f"Ваш чат откреплен от группы {select_group(group_id)['name']}")

    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def send_schedule(call):
    group_id = call.data.split("_")[1]
    today_only = True if call.data.split("_")[2] == "today" else False
    if call.data.split("_")[3] == "numerator":
        is_numerator = 1 
    elif call.data.split("_")[3] == "denominator":
        is_numerator = 0 
    else:
        is_numerator = -1

    schedule_text = get_schedule(url, group_id, is_numerator, today_only)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if is_numerator == -1:
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    bot.send_message(call.message.chat.id, schedule_text, reply_markup=keyboard_numerator(is_numerator, group_id))

    bot.answer_callback_query(call.id)

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
    

    
    if message.text == "Привет":
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")
    if message.text == "Пока":
        bot.reply_to(
            message,
            f"Досвидания, {message.from_user.first_name}.\nБуду скучать!",
        )


bot.infinity_polling()
