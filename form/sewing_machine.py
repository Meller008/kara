from form.templates import list, table
from my_class.orm_class import ManufacturerSewingMachine, TypeSewingMachine, SewingMachine
from PyQt5.uic import loadUiType
from PyQt5.QtCore import Qt
from os import getcwd
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from pony.orm import *


COLOR_WINDOW_MANUFACTURER = "102, 0, 255"
COLOR_WINDOW_TYPE = "51, 51, 255"
COLOR_WINDOW_MACHINE = "102, 153, 255"


main_class = loadUiType(getcwd() + '/ui/sewing_machine.ui')[0]


class SewingMachineList(table.TableList):
    def set_settings(self):

        self.setWindowTitle("Поставщики")  # Имя окна
        self.resize(400, 270)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_MACHINE)  # Цвет бара

        self.pb_copy.deleteLater()
        self.pb_other.deleteLater()
        self.pb_filter.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Название", 100), ("Промзводитель", 100))

        self.item = SewingMachine  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = select((s.id, s.name, s.manufacturer.name) for s in SewingMachine)

    def ui_add_table_item(self):  # Добавить предмет
        self.machine_window = SewingMachineBrows(self)
        self.machine_window.setWindowModality(Qt.ApplicationModal)
        self.machine_window.show()

    def ui_change_table_item(self, id=False):  # изменить элемент
        if id:
            item_id = id
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


class SewingMachineBrows(QMainWindow, main_class):
    def __init__(self, main=None, machine_id=None):
        super(SewingMachineBrows, self).__init__()
        self.setupUi(self)
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
