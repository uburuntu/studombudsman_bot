# -*- coding: utf-8 -*-
import json

import config
from fs_interface import FileSystemInterface
from utils import global_lock, is_non_zero_file


# TODO: use database
class UsersController:
    def __init__(self, file_name=config.file_location['user_data']):
        self.file_name = file_name
        self.data = dict()
        self.load()

    def load(self):
        if is_non_zero_file(self.file_name):
            global_lock.acquire()
            with open(self.file_name, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
            global_lock.release()

    def save(self):
        global_lock.acquire()
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=True)
        global_lock.release()

    def start_session(self, message):
        self.data[str(message.from_user.id)] = dict()
        self.data[str(message.from_user.id)]['deep'] = 0
        self.data[str(message.from_user.id)]['path'] = "./File"
        self.save()

    def go_to_dir(self, message):
        if message.text in self.print_path(message.from_user):
            self.data[str(message.from_user.id)]['deep'] += 1
            x = FileSystemInterface(self.data[str(message.from_user.id)]['path'])
            self.data[str(message.from_user.id)]['path'] = x.go(message.text).my_name()
            self.save()
        else:
            print("Попытка взлома", str(message.from_user.id))

    def get_file_name(self, message):
        x = FileSystemInterface(self.data[str(message.from_user.id)]['path'])
        return x.go(message.text).my_name()

    def other_get_file_name(self, message):
        x = FileSystemInterface(self.data[str(message.from_user.id)]['path'])
        return x.go('').my_name()

    def get_back(self, message):
        if self.data[str(message.from_user.id)]['deep'] > 0:
            self.data[str(message.from_user.id)]['deep'] += -1
            self.data[str(message.from_user.id)]['path'] = FileSystemInterface(
                self.data[str(message.from_user.id)]['path']).back().my_name()
            self.save()
        else:
            print("Попытка взлома", str(message.from_user.id))

    def this_child_dir(self, message):
        x = FileSystemInterface(self.data[str(message.from_user.id)]['path'])
        y = x.go(message.text)
        return y.i_am_dir()

    def print_path(self, user):
        s = []
        for it in FileSystemInterface(self.data[str(user.id)]['path']).my_children():
            s.append(it.my_short())
        return s

    def can_get_back(self, message):
        return self.data[str(message.from_user.id)]['deep'] > 0
