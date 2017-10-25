from os import getcwd
import re
from datetime import date
from decimal import Decimal
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QDialog, QListWidgetItem
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtCore import Qt
from form.templates import table
from form import payment, shipping
from my_class.orm_class import Vendor, Country, PaymentMethod, ShippingMethod
from pony.orm import *


vendor_class = loadUiType(getcwd() + '/ui/vendor_brows.ui')[0]


COLOR_WINDOW = "153, 102, 204"


class VendorList(table.TableList):
    def set_settings(self):

        self.setWindowTitle("Поставщики")  # Имя окна
        self.resize(400, 270)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.pb_copy.deleteLater()
        self.pb_other.deleteLater()
        self.pb_filter.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Название", 100), ("Почта", 100), ("Сайт", 100))

        self.item = Vendor  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = select((v.id, v.name, v.mail, v.site) for v in Vendor)

    def ui_add_table_item(self):  # Добавить предмет
        self.vendor_window = VendorBrows(self)
        self.vendor_window.setModal(True)
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

        self.vendor_window = VendorBrows(self, item_id)
        self.vendor_window.setModal(True)
        self.vendor_window.show()


class VendorBrows(QDialog, vendor_class):
    def __init__(self, main=None, ven_id=None):
        super(VendorBrows, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)

        self.main = main
        self.id = ven_id
        self.vendor_class = None

        self.set_tart_settings()

    @db_session
    def set_tart_settings(self):

        if self.id:
            self.vendor_class = Vendor[int(self.id)]
            self.le_name.setText(self.vendor_class.name),
            self.le_full_name.setText(self.vendor_class.full_name),
            self.le_mail.setText(self.vendor_class.mail),
            self.le_note.setText(self.vendor_class.note),
            self.le_phone.setText(self.vendor_class.phone),
            self.le_site.setText(self.vendor_class.site),

        else:
            pass

        # Вставим страны
        for c in select(c for c in Country):
            self.cb_country.addItem(c.name, c.id)

    def ui_add_payment(self):
        self.pay_win = payment.PaymentMethodList(self, True)
        self.pay_win.setWindowModality(Qt.ApplicationModal)
        self.pay_win.show()

    def ui_add_shipping(self):
        self.ship_win = shipping.ShippingMethodList(self, True)
        self.ship_win.setWindowModality(Qt.ApplicationModal)
        self.ship_win.show()

    def ui_del_payment(self):
        row = self.lw_payment.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите способ который надо удалить", QMessageBox.Ok)
            return False

        self.lw_payment.takeItem(row)

    def ui_del_shipping(self):
        row = self.lw_shipping.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите способ который надо удалить", QMessageBox.Ok)
            return False

        self.lw_shipping.takeItem(row)

    @db_session
    def ui_acc(self):

        value = {
                "name": self.le_name.text(),
                "full_name": self.le_full_name.text(),
                "mail": self.le_mail.text(),
                "note": self.le_note.text(),
                "phone": self.le_phone.text(),
                "site": self.le_site.text(),
                "country": self.cb_country.currentData()
                }

        if self.vendor_class:
            self.vendor_class(**value)
        else:
            v = Vendor(**value)

        for row in range(self.lw_shipping.count()):
            v.shipping_methods.add(ShippingMethod[self.lw_shipping.item(row).data(5)])

        self.close()
        self.destroy()

    def ui_can(self):
        self.close()
        self.destroy()

    @db_session
    def of_list_select_payment_method(self, pay_id):
        method = PaymentMethod[pay_id]
        item = QListWidgetItem(method.name)
        item.setData(5, method.id)
        self.lw_payment.addItem(item)

    @db_session
    def of_list_select_shipping_method(self, ship_id):
        ship = ShippingMethod[ship_id]
        item = QListWidgetItem(ship.name)
        item.setData(5, ship.id)
        self.lw_shipping.addItem(item)

