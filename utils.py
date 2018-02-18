# _*_ coding: utf-8 _*_

import pickle
import re
import threading
from datetime import datetime
from os import path

import telebot

import config
import tokens

# Инициализация бота
bot = telebot.TeleBot(tokens.bot, threaded=False)
bot_name = '@' + bot.get_me().username

global_lock = threading.Lock()
message_dump_lock = threading.Lock()


def commands_handler(commands):
    def wrapped(message):
        if not message.text:
            return False
        split_message = re.split(r'[^\w@/]', message.text.lower())
        s = split_message[0]
        return (s in commands) or (s.endswith(bot_name) and s.split('@')[0] in commands)

    return wrapped


def curr_time():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')


def user_name(user):
    first_name = user.first_name
    last_name = ' ' + user.last_name if isinstance(user.last_name, str) else ''
    return first_name + last_name


def user_info(user):
    # Required fields
    user_id = str(user.id)
    first_name = user.first_name
    # Optional fields
    last_name = ' ' + user.last_name if isinstance(user.last_name, str) else ''
    username = ', @' + user.username if isinstance(user.username, str) else ''
    language_code = ', ' + user.language_code if isinstance(user.language_code, str) else ''
    # Output
    return user_id + ' (' + first_name + last_name + username + language_code + ')'


def chat_info(chat):
    if chat.type == 'private':
        return 'private'
    else:
        return chat.type + ': ' + chat.title + ' (' + str(chat.id) + ')'


def action_log(text):
    print("{}\n{}\n".format(curr_time(), text))


def user_action_log(message, text):
    print("{}, {}\nUser {} {}\n".format(curr_time(), chat_info(message.chat), user_info(message.from_user), text))


def is_command():
    def wrapped(message):
        if not message.text or not message.text.startswith('/'):
            return False
        return True

    return wrapped


def bot_admin_command(func):
    def wrapped(message):
        if message.from_user.id in config.admin_ids:
            return func(message)
        return

    return wrapped


def command_with_delay(delay=10):
    def my_decorator(func):
        def wrapped(message):
            if message.chat.type != 'private':
                now = datetime.now().timestamp()
                diff = now - func.last_call if hasattr(func, 'last_call') else now
                if diff < delay:
                    user_action_log(message, "called {} after {} sec, delay is {}".format(func, round(diff), delay))
                    return
                func.last_call = now

            return func(message)

        return wrapped

    return my_decorator


def cut_long_text(text, max_len=4250):
    """
    Функция для нарезки длинных сообщений по переносу строк или по точке в конце предложения или по пробелу
    :param text: тескт для нарезки
    :param max_len: длина, которую нельзя превышать
    :return: список текстов меньше max_len, суммарно дающий text
    """
    last_cut = 0
    space_anchor = 0
    dot_anchor = 0
    nl_anchor = 0

    if len(text) < max_len:
        yield text[last_cut:]
        return

    for i in range(len(text)):
        if text[i] == '\n':
            nl_anchor = i + 1
        if text[i] == '.' and text[i + 1] == ' ':
            dot_anchor = i + 2
        if text[i] == ' ':
            space_anchor = i

        if i - last_cut > max_len:
            if nl_anchor > last_cut:
                yield text[last_cut:nl_anchor]
                last_cut = nl_anchor
            elif dot_anchor > last_cut:
                yield text[last_cut:dot_anchor]
                last_cut = dot_anchor
            elif space_anchor > last_cut:
                yield text[last_cut:space_anchor]
                last_cut = space_anchor
            else:
                yield text[last_cut:i]
                last_cut = i

            if len(text) - last_cut < max_len:
                yield text[last_cut:]
                return

    yield text[last_cut:]


def value_from_file(file_name, default=0):
    value = default
    if path.isfile(file_name):
        global_lock.acquire()
        with open(file_name, 'r', encoding='utf-8') as file:
            file_data = file.read()
            if file_data.isdigit():
                value = int(file_data)
        global_lock.release()
    return value


def value_to_file(file_name, value):
    global_lock.acquire()
    with open(file_name, 'w+', encoding='utf-8') as file:
        file.write(str(value))
    global_lock.release()


def char_escaping(text, mode='html'):
    # TODO: markdown
    if mode.lower() == 'html':
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
    return text


def dump_messages(all_messages):
    groups = {}
    for message in all_messages:
        dump_filename = config.dump_dir + 'dump_' + message.chat.type + '_' + str(message.chat.id) + '.pickle'
        if dump_filename in groups:
            lst = groups[dump_filename]
        else:
            lst = []
            groups[dump_filename] = lst
        lst.append(message)

    message_dump_lock.acquire()
    for dump_filename, messages in groups.items():
        if path.isfile(dump_filename):
            f = open(dump_filename, 'rb+')
            try:
                file_messages = pickle.load(f)
            except EOFError:
                file_messages = []
            file_messages.extend(messages)
            f.seek(0)
            f.truncate()
        else:
            f = open(dump_filename, 'xb')
            file_messages = messages
        pickle.dump(file_messages, f, pickle.HIGHEST_PROTOCOL)
        f.close()
    message_dump_lock.release()


def bold(text, mode="html"):
    if mode.lower() == "html":
        return "<b>{}</b>".format(text)
    if mode.lower() == "markdown":
        return "*{}*".format(text)


def link(text, user_id, mode="html"):
    if mode.lower() == "html":
        return "<a href=\"tg://user?id={0}\">{1}</a>".format(user_id, text)
    if mode.lower() == "markdown":
        return "[{1}](tg://user?id={0})".format(user_id, text)


def link_user(user, mode="html"):
    if mode.lower() == "html":
        return "<a href=\"tg://user?id={0}\">{1}</a>".format(user.id, user_name(user))
    if mode.lower() == "markdown":
        return "[{1}](tg://user?id={0})".format(user.id, user_name(user))
