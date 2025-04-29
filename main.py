import telebot
import config
from DataBase import *
from functions import *
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
        bot.send_message(message.chat.id, "Добро пожаловать в ЭДС!", reply_markup=keyboard_commands)
        # bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)
        user_first_name = message.from_user.first_name if message.from_user.first_name != None else ""
        user_last_name = message.from_user.last_name if message.from_user.last_name != None else ""
        user_name = user_first_name + user_last_name if user_first_name + user_last_name != "" else message.from_user.username
        add_user(user_id, user_name)
    else:
        bot.send_message(message.chat.id, f"Рады видеть вас снова, {message.from_user.first_name}!", reply_markup=keyboard_commands)


@bot.message_handler(commands=["schedule"])
def send_schedule_simple(message):
        # Разбираем текст сообщения
        command, *args = message.text.split()
        if len(args) < 1:
            bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=keyboard_groups_week)
            return
        else: 
            group_name = args[0].upper()  # Название группы
            today_only = False
            
            # Проверяем, запрошено ли расписание только на сегодня
            if len(args) > 1 and args[1].lower() == "today":
                today_only = True
            
            # Получаем расписание
            schedule_text = get_schedule(url, group_name, today_only)
            
            # Отправляем расписание пользователю
            bot.reply_to(message, schedule_text)

@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def send_schedule(call):
    group_name = call.data.split("_")[1]
    today_only = True if call.data.split("_")[2] == "today" else False

    schedule_text = get_schedule(url, group_name, today_only)

    bot.send_message(call.message.chat.id, schedule_text)

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
    if message.text in ["🗓️ Расписание занятий НТИ", "Расписание занятий НТИ", "🗓️"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=keyboard_groups_week)
        return
    if message.text in ["📅 Расписание на сегодня", "Расписание на сегодня", "📅"]:
        bot.reply_to(message, "Пожалуйста, выберите группу или введите номер в комманду. \n<i>Пример: /schedule Т-143901-ИСТ</i>", reply_markup=keyboard_groups_today)
        return
    if message.text == "Привет":
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")
    if message.text == "Пока":
        bot.reply_to(
            message,
            f"Досвидания, {message.from_user.first_name}.\nБуду скучать!",
        )


bot.infinity_polling()
