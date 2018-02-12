# -*- coding: utf-8 -*- 

import telebot
from telebot import types

import Tokens
from UsersController import UsersController

botan_key = Tokens.botan

bot = telebot.TeleBot(Tokens.bot)

people = set()
current_controller = UsersController()


def build_child(message):
    s = current_controller.print_path(message.from_user)
    keyboard = types.ReplyKeyboardMarkup()
    # s.sort()
    if current_controller.can_get_back(message) == False:
        keyboard.row('1', '2', '3')
        keyboard.row('4', '5', '6')
        keyboard.row('7', '8', '9')
    else:
        kook = False
        for name in s:
            if name != '.DS_Store' and name != 'main.txt':
                kook = True
                # keyboard.add(types.KeyboardButton(name))
        if kook:
            keyboard.row('Да', 'Нет')
    # print(current_controller.print_path(message.from_user))
    # newpath = current_controller.other_get_file_name(message)
    # newpath = newpath + '/kek'
    # if not os.path.exists(newpath): os.makedirs(newpath)
    if current_controller.can_get_back(message):
        back = types.KeyboardButton('Назад')
        keyboard.row(back)
    if current_controller.can_get_back(message):
        back = types.KeyboardButton('В начало')
        keyboard.row(back)

    news = current_controller.other_get_file_name(message)
    my_file = open(news + '/' + 'main.txt')
    my_string = my_file.read()
    msg = bot.send_message(message.chat.id, my_string, reply_markup=keyboard)
    print(msg)
    print(current_controller.other_get_file_name(message))
    bot.register_next_step_handler(msg, where)


def where(message):
    s = str()
    for it in message.text:
        if it != '/':
            s = s + it
    message.text = s
    if message.text == 'Назад':
        current_controller.get_back(message)
    elif message.text == 'В начало':
        current_controller.start_session(message)
    else:
        if current_controller.this_child_dir(message):
            current_controller.go_to_dir(message)
        else:
            return build_child(message)
    build_child(message)


@bot.message_handler(commands=['start'])
def start(mes):
    if (mes.chat.type != 'private'):
        return
    if (mes.from_user.id in people):
        return
    people.add(mes.from_user.id)
    current_controller.start_session(mes)
    build_child(mes)


bot.polling()
