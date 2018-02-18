#  -*- coding: utf-8 -*-

import os
import time

from requests import ReadTimeout
from telebot import types

from commands import admin_tools
from users_controller import UsersController
from utils import bot, action_log, dump_messages, global_lock, message_dump_lock, user_action_log, bot_admin_command, \
    bot_name, commands_handler, botan

people = set()
current_controller = UsersController()


def build_child(message):
    s = current_controller.print_path(message.from_user)
    keyboard = types.ReplyKeyboardMarkup()
    # s.sort()
    if current_controller.can_get_back(message) is False:
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
    my_file = open(news + '/' + 'main.txt', encoding='utf-8')
    my_string = my_file.read()
    msg = bot.send_message(message.chat.id, my_string, reply_markup=keyboard)

    user_action_log(message, 'now in ' + news)
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
    if mes.chat.type != 'private':
        return
    if mes.from_user.id in people:
        return
    people.add(mes.from_user.id)
    current_controller.start_session(mes)
    build_child(mes)


@bot.message_handler(func=commands_handler(['/update']))
@bot_admin_command
def command_update(message):
    user_action_log(message, "called: " + message.text)
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != bot_name:
        return
    admin_tools.update_bot(message)


@bot.message_handler(func=commands_handler(['/kill']))
@bot_admin_command
def command_kill(message):
    user_action_log(message, "called: " + message.text)
    parts = message.text.split()
    if len(parts) < 2 or parts[1] != bot_name:
        return
    admin_tools.kill_bot(message)


# All messages handler
def handle_messages(messages):
    for message in messages:
        botan.track(message)
    dump_messages(messages)


while __name__ == '__main__':
    try:
        action_log("Running bot!")

        # Запуск Long Poll бота
        bot.set_update_listener(handle_messages)
        bot.polling(none_stop=True, timeout=60)
        time.sleep(1)

    # из-за Telegram API иногда какой-нибудь пакет не доходит
    except ReadTimeout as e:
        action_log("Read Timeout. Because of Telegram API. We are offline. Reconnecting in 5 seconds.")
        time.sleep(5)

    # если пропало соединение, то пытаемся снова
    except ConnectionError as e:
        action_log("Connection Error. We are offline. Reconnecting...")
        time.sleep(5)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RecursionError as e:
        action_log("Recursion Error. Restarting...")
        global_lock.acquire()
        message_dump_lock.acquire()
        os._exit(0)

    # если Python сдурит и пойдёт в бесконечную рекурсию (не особо спасает)
    except RuntimeError as e:
        action_log("Runtime Error. Retrying in 5 seconds.")
        time.sleep(5)

    # кто-то обратился к боту на кириллице
    except UnicodeEncodeError as e:
        action_log("Unicode Encode Error. Retrying in 5 seconds.")
        time.sleep(5)

    # завершение работы из консоли стандартным Ctrl-C
    except KeyboardInterrupt as e:
        action_log("Keyboard Interrupt. Good bye.")
        global_lock.acquire()
        message_dump_lock.acquire()
        os._exit(0)
