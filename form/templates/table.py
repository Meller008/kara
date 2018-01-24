from os import getcwd
from decimal import Decimal
from datetime import date
import re
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
from function import to_excel, table_to_html
from my_class import print_qt, orm_class
from pony.orm import *


COLOR_WINDOW = "255, 255, 255"


class TableList(QMainWindow):
    def __init__(self, main_class=0, dc_select=False, other=None):
        super(TableList, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/table/table.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.main = main_class
        self.dc_select = dc_select
        self.other_value = other

        self.set_settings()
        self.set_table_header()
        self.set_table_info()

    def set_settings(self):
        self.setWindowTitle("Список")  # Имя окна
        self.resize(720, 270)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Название", 120), ("Почта", 170), ("Сайт", 170))

        self.item = orm_class.Vendor  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = select((v.id, v.name, v.mail, v.site) for v in orm_class.Vendor)

    def set_table_header(self):
        i = 0
        self.table_widget.clear()
        for headet_item in self.table_header_name:
            self.table_widget.insertColumn(i)
            self.table_widget.setHorizontalHeaderItem(i, QTableWidgetItem(headet_item[0]))
            self.table_widget.horizontalHeader().resizeSection(i, int(headet_item[1]))
            i += 1

    @db_session
    def set_table_info(self):

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        list_table_item = self.query[:]

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

    def ui_add_table_item(self):  # Добавить предмет
        id = False
        pass

    def ui_change_table_item(self, id=False):  # изменить элемент
        if id:
            item_id = id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
                return False

        pass

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            # что хотим получить ставим всместо 0
            item = (self.table_widget.item(item.row(), 0).text(), item.data(5))
            self.main.of_tree_select_operation(item)
            self.close()
            self.destroy()

    @db_session
    def ui_dell_table_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить элемент?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                id_item = self.table_widget.selectedItems()
            except:
                QMessageBox.critical(self, "Ошибка Удаления", "Выделите элемент который хотите удалить", QMessageBox.Ok)
                return False
            try:
                self.item[id_item[0].data(5)].delete()
            except ConstraintError:
                QMessageBox.critical(self, "Ошибка Удаления", "Этот элемент уже используется", QMessageBox.Ok)
                return False
            commit()
            self.set_table_info()

    def ui_update(self):
        self.table_widget.setSortingEnabled(False)
        self.set_table_info()
        self.table_widget.setSortingEnabled(True)

    def ui_duplicate_table_item(self):
        pass

    def ui_filter(self):
        pass

    def ui_other(self):
        pass

    def ui_print(self):
        head = self.windowTitle()
        html = table_to_html.tab_html(self.table_widget, table_head=head)
        self.print_class = print_qt.PrintHtml(self, html)

    def ui_export(self):
        path = QFileDialog.getSaveFileName(self, "Сохранение")
        if path[0]:
            to_excel.table_to_excel(self.table_widget, path[0])