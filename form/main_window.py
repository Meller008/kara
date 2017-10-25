from os import getcwd
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
from form import country

main_class = loadUiType(getcwd() + '/ui/main_window.ui')[0]


class MainWindow(QMainWindow, main_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.show()

    def ui_view_country(self):
        self.country = country.CountryList()
        self.sub_country = QMdiSubWindow()
        self.sub_country.setWidget(self.country)
        self.mdi.addSubWindow(self.sub_country)
        self.sub_country.resize(self.country.size())
        self.sub_country.show()