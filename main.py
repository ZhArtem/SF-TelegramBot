import telebot
from telebot import types
from config import TOKEN, currencies
from extensions import Converter, APIException


def create_markup(hid=None):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = []
    for curr in currencies.keys():
        if curr != hid:
            buttons.append(types.KeyboardButton(curr.capitalize()))
    markup.add(*buttons)
    return markup


def commands_markup():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    buttons = ['/convert', '/values', '/help']
    markup.add(*buttons)
    return markup


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def start(message: telebot.types.Message):
    text = 'Бот производит конвертацию из одной валюты в другую.\n\nСписок доступных для конвертации валют: /values\n\
Для конвертации, воспользуйтесь командой /convert или напишите боту в следующем формате:\n\n<имя валюты> \
<в какую валюту перевести> <количество переводимой валюты>\n\nДоступные команды:\n/convert - конвертация.\n/values - \
список доступных валют.\n/help - помощь.'
    bot.send_message(message.chat.id, text, reply_markup=commands_markup())


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for i in currencies.keys():
        text = '\n'.join((text, i))
    bot.reply_to(message, text, reply_markup=commands_markup())


@bot.message_handler(commands=['convert'])
def convert(message: telebot.types.Message):
    text = 'Выберете валюту из которой конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, from_handler)


def from_handler(message: telebot.types.Message):
    curr_from = message.text
    text = 'Выберете валюту в которую конвертировать:'
    bot.send_message(message.chat.id, text, reply_markup=create_markup(hid=curr_from))
    bot.register_next_step_handler(message, to_handler, curr_from)


def to_handler(message: telebot.types.Message, curr_from):
    curr_to = message.text
    text = 'Напишите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, curr_from, curr_to)


def amount_handler(message: telebot.types.Message, curr_from, curr_to):
    amount = message.text.strip()
    try:
        conv = Converter.get_convert(curr_from, curr_to, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка в конвертации:\n{e}')
    else:
        answer_text = f'Стоимость {amount} едениц валюты {curr_from} в валюте {curr_to}: {conv}\n{amount} \
{currencies[curr_from]} = {conv} {currencies[curr_to]}'
        bot.send_message(message.chat.id, answer_text, reply_markup=commands_markup())


@bot.message_handler(content_types=['text'])
def converter(message: telebot.types.Message):
    try:
        curr_from, curr_to, amount = message.text.split()
    except ValueError:
        bot.reply_to(message, 'Неверное количество параметров!\nПравильный формат команды для бота можно посмотреть в \
/help. Или воспользуйся командой /convert.')
    else:
        curr_from = curr_from.capitalize()
        curr_to = curr_to.capitalize()
        try:
            conv = Converter.get_convert(curr_from, curr_to, amount)
            answer_text = f'Стоимость {amount} едениц валюты {curr_from} в валюте {curr_to}: {conv}\n{amount} \
{currencies[curr_from]} = {conv} {currencies[curr_to]}'
            bot.reply_to(message, answer_text)
        except APIException as e:
            bot.reply_to(message, f'Ошибка в команде:\n{e}')
        except Exception as e:
            bot.reply_to(message, f'Системная ошибка.\n{e}')


bot.polling()

