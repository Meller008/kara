from os import getcwd
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog


class Item2(QDialog):
    def __init__(self):
        super(Item2, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/list/item_2.ui', self)

    def set_settings(self, setting):
        for name, value in setting.items():
            if name == "WinTitle":
                self.setWindowTitle(value)
            elif name == "WinSize":
                self.resize(value)
            elif name == "WinColor":
                self.widget.setStyleSheet("background-color: rgb%s;" % value)
            else:
                getattr(self, name).setText(value)
