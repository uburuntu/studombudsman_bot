# -*- coding: utf-8 -*-

from pathlib import Path


class FileSystemInterface:
    def __init__(self, new_position="."):
        self.position = Path(new_position)

    def my_children(self):
        a = [x for x in self.position.iterdir()]
        b = []
        for i in a:
            b.append(FileSystemInterface(i))
        return b

    def i_am_dir(self):
        return self.position.is_dir()

    def my_name(self):
        return str(self.position.relative_to("."))

    def my_short(self):
        return self.position.name

    def go(self, name):
        return FileSystemInterface(self.my_name() + "/" + name)

    def back(self):
        return FileSystemInterface(str(self.position.parent.relative_to(".")))
