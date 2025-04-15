import telebot
import config
import json

bot = telebot.TeleBot(config.TG_API_TOKEN)

users = {}

keyboard1 = telebot.types.ReplyKeyboardMarkup(True)

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("/start", "/help", "/about")

simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)


def user_add(userId, groupId):
    data = {"user_id": userId, "group_id": groupId}
    with open("data/users.txt", "w") as json_file:
        json.dump(data, json_file)


def users_update():
    global users
    with open("data/users.txt") as json_file:
        users = json.load(json_file)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    global users
    users_update()
    bot.send_message(message.chat.id, "Добро пожаловать в ЭДС!", reply_markup=keyboard1)
    if message.from_user.id not in users[1]:
        user_add(message.from_user.id, None)


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
