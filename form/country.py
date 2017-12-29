from os import getcwd
from form.templates import list
from my_class.orm_class import CityVendor, CountryVendor
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem, QDialog, QListWidgetItem
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon, QImage, QPixmap
from pony.orm import *

COLOR_WINDOW = "255, 255, 51"


city_class = loadUiType(getcwd() + '/ui/city.ui')[0]


class CountryVendorList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Страны поставщиков")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.item = CountryVendor

        self.set_new_win = {"WinTitle": "Страна",
                            "WinColor": "(%s)" % COLOR_WINDOW,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}


class CityVendorList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Города поставщиков")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.item = CityVendor

    def ui_add_item(self):
        add_item_window = CityVendorWindow()
        add_item_window.setModal(True)
        add_item_window.show()
        if add_item_window.exec() == 0:
            return False

        self.sql_set_list()

    def ui_change_item(self, sel_id=False):
        if sel_id:
            select_id = sel_id
        else:
            try:
                select_id = self.lw_list.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка", "Выберете элемент", QMessageBox.Ok)
                return False

        change_item_window = CityVendorWindow(select_id)
        change_item_window.setModal(True)
        change_item_window.show()
        if change_item_window.exec() == 0:
            return False

        self.sql_set_list()


class CityVendorWindow(QDialog, city_class):
    def __init__(self, city_id=None):
        super(CityVendorWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)

        self.id = city_id

        self.start()

    @db_session
    def start(self):
        for c in select(c for c in CountryVendor):
            self.cb_country.addItem(c.name, c.id)

        if self.id:
            city = CityVendor[self.id]
            self.le_name.setText(city.name)
            self.le_note.setText(city.note)
            self.cb_country.setCurrentText(self.city.country.name)

    @db_session
    def ui_acc(self):
        value = {
                "name": self.le_name.text(),
                "note": self.le_note.text(),
                "country": self.cb_country.currentData()
                }

        if self.id:
            c = CityVendor[self.id]
            c.set(**value)
        else:
            CityVendor(**value)

        self.done(1)
        self.close()
        self.destroy()

    def ui_can(self):
        self.close()
        self.destroy()




