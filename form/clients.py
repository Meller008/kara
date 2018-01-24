from os import getcwd
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from form.templates import table
from my_class.orm_class import Client, CityClient
from pony.orm import *

COLOR_WINDOW = "184, 134, 11"


class ClientList(table.TableList):
    def set_settings(self):
        self.setWindowTitle("Клиенты")  # Имя окна
        self.resize(400, 270)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.pb_copy.deleteLater()
        self.pb_other.deleteLater()
        self.pb_filter.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Клиент", 100), ("Почта", 100), ("Сайт", 100))

        self.item = Client  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = select((с.id, с.name, с.mail, с.site) for с in Client)

    def ui_add_table_item(self):  # Добавить предмет
        self.vendor_window = ClientBrows(self)
        self.vendor_window.setWindowModality(Qt.ApplicationModal)
        self.vendor_window.show()

    def ui_change_table_item(self, id=False):  # изменить элемент
        if id:
            item_id = id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
                return False

        self.vendor_window = ClientBrows(self, item_id)
        self.vendor_window.setWindowModality(Qt.ApplicationModal)
        self.vendor_window.show()

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            # что хотим получить ставим всместо 0
            self.main.of_select_client(item.data(5))
            self.close()
            self.destroy()


class ClientBrows(QMainWindow):
    def __init__(self, main=None, c_id=None):
        super(ClientBrows, self).__init__()
        loadUi(getcwd() + '/ui/client.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)

        self.main = main
        self.id = c_id

        self.start()

    @db_session
    def start(self):
        for c in select(c for c in CityClient):
            self.cb_city.addItem(c.name, c.id)

        if self.id:
            cl = Client[self.id]
            
            self.le_name.setText(cl.name)
            self.le_full_name.setText(cl.full_name)
            self.le_legal_address.setText(cl.addres_legal)
            self.le_actual_address.setText(cl.addres_actual)
            self.le_inn.setText(str(cl.inn))
            self.le_kpp.setText(str(cl.kpp))
            self.le_ogrn.setText(str(cl.ogrn))
            self.le_rs.setText(str(cl.account))
            self.le_bank.setText(cl.bank)
            self.le_ks.setText(str(cl.corres_account))
            self.le_bik.setText(str(cl.bik))
            self.le_fio.setText(cl.fio)
            self.le_phone.setText(cl.phone)
            self.le_mail.setText(cl.mail)
            self.le_site.setText(cl.site)
            self.le_note.setPlainText(cl.note)

            self.cb_city.setCurrentText(cl.city.name)

    @db_session
    def ui_acc(self):
        if not self.le_name.text():
            return False

        value = {
                "name": self.le_name.text(),
                "full_name": self.le_full_name.text(),
                "addres_legal": self.le_legal_address.text(),
                "addres_actual": self.le_actual_address.text(),
                "inn": self.le_inn.text(),
                "kpp": self.le_kpp.text(),
                "ogrn": self.le_ogrn.text(),
                "account": self.le_rs.text(),
                "bank": self.le_bank.text(),
                "corres_account": self.le_ks.text(),
                "bik": self.le_bik.text(),
                "fio": self.le_fio.text(),
                "phone": self.le_phone.text(),
                "mail": self.le_mail.text(),
                "site": self.le_site.text(),
                "note": self.le_note.toPlainText(),
                "city": self.cb_city.currentData()
                }

        if self.id:
            c = Client[self.id]
            c.set(**value)
        else:
            Client(**value)

        self.main.ui_update()
        self.close()
        self.destroy()

    def ui_can(self):
        self.close()
        self.destroy()