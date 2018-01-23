from os import getcwd
from decimal import Decimal
from datetime import date
import re
from pony.orm import *
from my_class.orm_class import ManufacturerSewingMachine, TypeSewingMachine, SewingMachine
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem, QTableWidgetItem
from PyQt5.QtGui import QIcon
from form.templates import list, table

COLOR_WINDOW_MANUFACTURER = "102, 0, 255"
COLOR_WINDOW_TYPE = "51, 51, 255"
COLOR_WINDOW_MACHINE = "102, 153, 255"

db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class SewingMachineList(table.TableList):
    def set_settings(self):

        self.setWindowTitle("Оборудование")  # Имя окна
        self.resize(450, 400)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_MACHINE)  # Цвет бара

        self.pb_copy.deleteLater()
        self.pb_other.deleteLater()
        self.pb_filter.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Название", 100), ("Производитель", 100), ("Типы", 200))

        self.item = SewingMachine  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = """SELECT sewingmachine.id, sewingmachine.name, manufacturersewingmachine.name, GROUP_CONCAT(typesewingmachine.name)
                        FROM typesewingmachine
                          LEFT JOIN sewingmachine_typesewingmachine ON typesewingmachine.id = sewingmachine_typesewingmachine.typesewingmachine
                          LEFT JOIN sewingmachine ON sewingmachine_typesewingmachine.sewingmachine = sewingmachine.id
                          LEFT JOIN manufacturersewingmachine ON sewingmachine.manufacturer = manufacturersewingmachine.id
                          GROUP BY sewingmachine"""

    def ui_add_table_item(self):  # Добавить предмет
        self.machine_window = SewingMachineBrows(self)
        self.machine_window.setWindowModality(Qt.ApplicationModal)
        self.machine_window.show()

    def ui_change_table_item(self, item_id=False):  # изменить элемент
        if item_id:
            item_id = item_id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
                return False

        self.machine_window = SewingMachineBrows(self, item_id)
        self.machine_window.setWindowModality(Qt.ApplicationModal)
        self.machine_window.show()

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            # что хотим получить ставим всместо 0
            self.main.of_select_sewing_machine(item.data(5))
            self.close()
            self.destroy()

    @db_session
    def set_table_info(self):

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        list_table_item = db.select(self.query)

        for table_typle in list_table_item:
            self.table_widget.insertRow(self.table_widget.rowCount())
            for column in range(1, len(table_typle)):
                if isinstance(table_typle[column], Decimal):
                    text = re.sub(r'(?<=\d)(?=(\d\d\d)+\b.)', ' ', str(table_typle[column]))
                elif isinstance(table_typle[column], date):
                    text = table_typle[column].strftime("%d.%m.%Y")
                else:
                    text = str(table_typle[column])
                item = QTableWidgetItem(text)
                item.setData(5, table_typle[0])
                self.table_widget.setItem(self.table_widget.rowCount() - 1, column - 1, item)


class SewingMachineBrows(QMainWindow):
    def __init__(self, main=None, machine_id=None):
        super(SewingMachineBrows, self).__init__()
        loadUi(getcwd() + '/ui/sewing_machine.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_MACHINE)

        self.main = main
        self.id = machine_id
        self.del_type = []

        self.set_tart_settings()

    @db_session
    def set_tart_settings(self):
        # Вставим страны
        for c in select(c for c in ManufacturerSewingMachine):
            self.cb_manufacturer.addItem(c.name, c.id)

        if self.id:
            self.machine_class = SewingMachine[int(self.id)]
            self.le_name.setText(self.machine_class.name)
            self.le_note.setText(self.machine_class.note)
            self.cb_manufacturer.setCurrentText(self.machine_class.manufacturer.name)

            for type in self.machine_class.type:
                item = QListWidgetItem(type.name)
                item.setData(5, type.id)
                self.lw_type.addItem(item)

        else:
            pass

    def ui_add_type(self):
        self.type_win = TypeMachineList(self, True)
        self.type_win.setWindowModality(Qt.ApplicationModal)
        self.type_win.show()

    def ui_del_type(self):
        row = self.lw_type.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите тип который надо удалить", QMessageBox.Ok)
            return False

        self.del_type.append(self.lw_type.item(row).data(5))
        self.lw_type.takeItem(row)

    @db_session
    def of_list_select_type_machine(self, type_id):
        type = TypeSewingMachine[type_id]
        item = QListWidgetItem(type.name)
        item.setData(5, type.id)
        self.lw_type.addItem(item)

    @db_session
    def ui_acc(self):
        value = {
            "name": self.le_name.text(),
            "note": self.le_note.text(),
            "manufacturer": self.cb_manufacturer.currentData()
        }

        if self.id:
            machine_class = SewingMachine[self.id]
            machine_class.set(**value)
        else:
            machine_class = SewingMachine(**value)

        machine_class.type.remove(map(lambda x: TypeSewingMachine[x], self.del_type))
        machine_class.type.add(map(lambda row: TypeSewingMachine[self.lw_type.item(row).data(5)], range(self.lw_type.count())))

        self.main.ui_update()
        self.close()
        self.destroy()


class TypeMachineList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Типы машин")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_TYPE)  # Цвет бара

        self.item = TypeSewingMachine

        self.set_new_win = {"WinTitle": "Тип машины",
                            "WinColor": "(%s)" % COLOR_WINDOW_TYPE,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_type_machine(select_prov.data(5))
            self.close()
            self.destroy()


class ManufacturerMachineList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Производители машин")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_MANUFACTURER)  # Цвет бара

        self.item = ManufacturerSewingMachine

        self.set_new_win = {"WinTitle": "Производитель",
                            "WinColor": "(%s)" % COLOR_WINDOW_MANUFACTURER,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_manufacturer_machine(select_prov.data(5))
            self.close()
            self.destroy()
