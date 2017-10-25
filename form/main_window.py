from os import getcwd
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow, QLabel
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon, QBrush, QImage
import sys

main_class = loadUiType(getcwd() + '/ui/main_window.ui')[0]


class MainWindow(QMainWindow, main_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.setupUi(self)
        self.show()

    def ui_view_country(self):
        self.country = supply_material.MaterialSupplyList()
        self.sub_country = QMdiSubWindow()
        self.sub_country.setWidget(self.country)
        self.mdi.addSubWindow(self.sub_country)
        self.sub_country.resize(self.country.size())
        self.sub_country.show()