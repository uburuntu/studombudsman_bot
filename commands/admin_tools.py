# !/usr/bin/env python
# _*_ coding: utf-8 _*_
import os

import config
from utils import bot, value_to_file


def kill_bot(message):
    if not hasattr(kill_bot, "check_sure"):
        kill_bot.check_sure = True
        bot.reply_to(message, "Are you sure?")
        return
    value_to_file(config.file_location['bot_killed'], 1)
    bot.reply_to(message, "Ух, ухожу на отдых...")
    os._exit(0)


def update_bot(message):
    if not hasattr(update_bot, "check_sure"):
        update_bot.check_sure = True
        bot.reply_to(message, "Are you sure?")
        return
    bot.reply_to(message, "Ух, ухожу на обновление...")
    os.execl('/bin/bash', 'bash', 'bot_update.sh')
