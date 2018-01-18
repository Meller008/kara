from os import getcwd
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox, QDialog, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from form.templates import table
from form import payment, shipping
from my_class.orm_class import Vendor, CityVendor, PaymentMethodVendor, ShippingMethodVendor
from pony.orm import *

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

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            # что хотим получить ставим всместо 0
            self.main.of_select_vendor(item.data(5))
            self.close()
            self.destroy()


class VendorBrows(QDialog):
    def __init__(self, main=None, ven_id=None):
        super(VendorBrows, self).__init__()
        loadUi(getcwd() + '/ui/vendor_brows.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)

        self.main = main
        self.id = ven_id
        self.del_shipping = []
        self.del_payment = []

        self.set_tart_settings()

    @db_session
    def set_tart_settings(self):
        # Вставим страны
        for c in select(c for c in CityVendor):
            self.cb_country.addItem(c.name, c.id)

        if self.id:
            self.vendor_class = Vendor[int(self.id)]
            self.le_name.setText(self.vendor_class.name)
            self.le_full_name.setText(self.vendor_class.full_name)
            self.le_mail.setText(self.vendor_class.mail)
            self.le_note.setText(self.vendor_class.note)
            self.le_phone.setText(self.vendor_class.phone)
            self.le_site.setText(self.vendor_class.site)
            self.cb_country.setCurrentText(self.vendor_class.city.name)

            for ship in self.vendor_class.shipping_methods:
                item = QListWidgetItem(ship.name)
                item.setData(5, ship.id)
                self.lw_shipping.addItem(item)

            for pay in self.vendor_class.payment_methods:
                item = QListWidgetItem(pay.name)
                item.setData(5, pay.id)
                self.lw_payment.addItem(item)

        else:
            pass

    def ui_add_payment(self):
        self.pay_win = payment.PaymentMethodVendorList(self, True)
        self.pay_win.setWindowModality(Qt.ApplicationModal)
        self.pay_win.show()

    def ui_add_shipping(self):
        self.ship_win = shipping.ShippingMethodVendorList(self, True)
        self.ship_win.setWindowModality(Qt.ApplicationModal)
        self.ship_win.show()

    def ui_del_payment(self):
        row = self.lw_payment.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите способ который надо удалить", QMessageBox.Ok)
            return False

        self.del_payment.append(self.lw_payment.item(row).data(5))
        self.lw_payment.takeItem(row)

    def ui_del_shipping(self):
        row = self.lw_shipping.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите способ который надо удалить", QMessageBox.Ok)
            return False

        self.del_shipping.append(self.lw_shipping.item(row).data(5))
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
                "city": self.cb_country.currentData()
                }

        if self.id:
            v = Vendor[self.id]
            v.set(**value)
        else:
            v = Vendor(**value)

        v.shipping_methods.remove(map(lambda x: ShippingMethodVendor[x], self.del_shipping))
        v.payment_methods.remove(map(lambda x: PaymentMethodVendor[x], self.del_payment))

        for row in range(self.lw_shipping.count()):
            v.shipping_methods.add(ShippingMethodVendor[self.lw_shipping.item(row).data(5)])

        for row in range(self.lw_payment.count()):
            v.payment_methods.add(PaymentMethodVendor[self.lw_payment.item(row).data(5)])

        self.close()
        self.destroy()

    def ui_can(self):
        self.close()
        self.destroy()

    @db_session
    def of_list_select_payment_method(self, pay_id):
        method = PaymentMethodVendor[pay_id]
        item = QListWidgetItem(method.name)
        item.setData(5, method.id)
        self.lw_payment.addItem(item)

    @db_session
    def of_list_select_shipping_method(self, ship_id):
        ship = ShippingMethodVendor[ship_id]
        item = QListWidgetItem(ship.name)
        item.setData(5, ship.id)
        self.lw_shipping.addItem(item)


