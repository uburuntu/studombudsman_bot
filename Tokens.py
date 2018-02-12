# -*- coding: utf-8 -*-

import os

# Set your api tokens and keys through environmental variables
# (add lines to your .bashrc and restart terminal):
# export STUDOMBUDSMAN_BOT_TOKEN="XXXXX:XXXXXXXXXXX"
# export STUDOMBUDSMAN_BOTAN_TOKEN="XXX-XXX-XXX-XXXX"
#
# OR
#
# Manually through defaults in this file
# Important: untrack file to prevent accidential private token pushing:
# 'git update-index --assume-unchanged Tokens.py'

default_bot = ""
bot = os.getenv('STUDOMBUDSMAN_BOT_TOKEN', default_bot)

default_botan = ""
botan = os.getenv('STUDOMBUDSMAN_BOTAN_TOKEN', default_botan)
