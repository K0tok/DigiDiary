import telebot
import config
import json

bot = telebot.TeleBot(config.TG_API_TOKEN)

keyboard1 = telebot.types.ReplyKeyboardMarkup(True)

keyboard_commands = telebot.types.ReplyKeyboardMarkup(True)
keyboard_commands.row("/start", "/help", "/about")

simpleAnswerKeyboard = telebot.types.InlineKeyboardMarkup()
yesButton = telebot.types.InlineKeyboardButton("Да", callback_data="yes")
noButton = telebot.types.InlineKeyboardButton("Нет", callback_data="no")
simpleAnswerKeyboard.row(yesButton, noButton)


# def user_add(userId, groupId):

# def users_update(): 

user_id = 1

@bot.message_handler(commands=["start"])
def send_welcome(message):
    global user_id
    bot.send_message(message.chat.id, "Добро пожаловать в ЭДС!", reply_markup=keyboard1)
    bot.send_message(message.chat.id, f"{message.chat.id}" , reply_markup=keyboard1)
    user_id = message.from_user.id
    bot.send_message(message.chat.id, f'Ваш айди: {user_id}')

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
