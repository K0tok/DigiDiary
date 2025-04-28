import telebot
import config
from DataBase import *
from functions import *

bot = telebot.TeleBot(config.TG_API_TOKEN)

keyboard1 = telebot.types.ReplyKeyboardMarkup(True)

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("/start", "/help", "/about")

simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)

url = "https://nti.urfu.ru/api/schedule/nti/1/1/4"

# @bot.message_handler(commands=["admin_test"])
# def test(message): 
    # print(message.from_user.id,
    #     message.from_user.first_name,
    #     message.from_user.last_name,
    #     message.from_user.username)

    # user_first_name = message.from_user.first_name if message.from_user.first_name != None else ""
    # user_last_name = message.from_user.last_name if message.from_user.last_name != None else ""
    # user_name = user_first_name + user_last_name
    # print(user_name)

@bot.message_handler(commands=["start"])
def send_welcome(message): 
    user_id = message.from_user.id
    if user_id not in select_users_tgId():
        bot.send_message(message.chat.id, "Добро пожаловать в ЭДС!", reply_markup=keyboard1)
        # bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)
        user_first_name = message.from_user.first_name if message.from_user.first_name != None else ""
        user_last_name = message.from_user.last_name if message.from_user.last_name != None else ""
        user_name = user_first_name + user_last_name if user_first_name + user_last_name != "" else message.from_user.username
        add_user(user_id, user_name)
    else:
        bot.send_message(message.chat.id, f"Рады видеть вас снова, {message.from_user.first_name}!", reply_markup=keyboard1)
        # bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)


@bot.message_handler(commands=["schedule"])
def send_schedule(message):
        global url
        # Разбираем текст сообщения
        command, *args = message.text.split()
        if len(args) < 1:
            bot.reply_to(message, "Пожалуйста, укажите название группы. Пример: /schedule Т-143901-ИСТ")
            return
        
        group_name = args[0].upper()  # Название группы
        today_only = False
        
        # Проверяем, запрошено ли расписание только на сегодня
        if len(args) > 1 and args[1].lower() == "today":
            today_only = True
        
        # Получаем расписание
        schedule_text = get_schedule(url, group_name, today_only)
        
        # Отправляем расписание пользователю
        bot.reply_to(message, schedule_text)


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
    if message.text == "Привет":
        bot.reply_to(message, f"Привет, {message.from_user.first_name}!")
    if message.text == "Пока":
        bot.reply_to(
            message,
            f"Досвидания, {message.from_user.first_name}.\nБуду скучать!",
        )


bot.infinity_polling()
