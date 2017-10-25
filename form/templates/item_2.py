from os import getcwd
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialog

item_2 = loadUiType(getcwd() + '/ui/templates ui/item_2.ui')[0]


class Item2(QDialog, item_2):
    def __init__(self):
        super(Item2, self).__init__()
        self.setupUi(self)

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
