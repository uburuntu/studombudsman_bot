# -*- coding: utf-8 -*-

from pathlib import Path

from file_system_interface import FileSystemInterface


class UsersController:
    pathUsers = dict()
    userdeep = dict()

    def start_session(self, message):
        self.userdeep[message.from_user.id] = 0
        self.pathUsers[message.from_user.id] = FileSystemInterface(Path("./File"))

    def go_to_dir(self, message):
        if message.text in self.print_path(message.from_user):
            self.userdeep[message.from_user.id] += 1
            x = self.pathUsers[message.from_user.id]
            self.pathUsers[message.from_user.id] = x.go(message.text)
        else:
            print("Попытка взлома", message.from_user.id)

    def get_file_name(self, message):
        x = self.pathUsers[message.from_user.id]
        return x.go(message.text).my_name()

    def other_get_file_name(self, message):
        x = self.pathUsers[message.from_user.id]
        return x.go('').my_name()

    def get_back(self, message):
        if self.userdeep[message.from_user.id] > 0:
            self.userdeep[message.from_user.id] += -1
            self.pathUsers[message.from_user.id] = self.pathUsers[message.from_user.id].back()
        else:
            print("Попытка взлома", message.from_user.id)

    def this_child_dir(self, message):
        x = self.pathUsers[message.from_user.id]
        y = x.go(message.text)
        return y.i_am_dir()

    def print_path(self, user):
        s = []
        for it in self.pathUsers[user.id].my_children():
            s.append(it.my_short())
        return s

    def can_get_back(self, mes):
        return self.userdeep[mes.from_user.id] > 0;
