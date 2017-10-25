from os import getcwd
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem, QMainWindow, QFileDialog
from PyQt5.QtGui import QIcon
from function import my_sql, to_excel, table_to_html
from classes import print_qt
from decimal import Decimal
import datetime
import re
from classes.my_class import User


table_list_class = loadUiType(getcwd() + '/ui/templates ui/table.ui')[0]


class TableList(QMainWindow, table_list_class):
    def __init__(self, main_class=0, dc_select=False, other=None):
        super(TableList, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.main = main_class
        self.dc_select = dc_select
        self.other_value = other
        self.set_settings()
        self.set_table_header()
        self.set_table_info()
        self.access()

    def access(self):
        for item in User().access_list(self.__class__.__name__):
            a = getattr(self, item["atr1"])
            if item["atr2"]:
                a = getattr(a, item["atr2"])

            if item["value"]:
                if item["value"] == "True":
                    val = True
                elif item["value"] == "False":
                    val = False
                else:
                    try:
                        val = int(item["value"])
                    except:
                        val = item["value"]
                a(val)
            else:
                a()

    def set_settings(self):
        self.setWindowTitle("Список")  # Имя окна
        self.resize(720, 270)
        self.toolBar.setStyleSheet("background-color: rgb(255, 255, 255);")  # Цвет бара

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("1", 120), ("2", 170), ("3", 70), ("4", 70), ("5", 50))

        #  нулевой элемент должен быть ID
        self.query_table_select = """SELECT `order`.Id, clients.Name, clients_actual_address.Name, `order`.Date_Order, `order`.Date_Shipment, `order`.Number_Doc,
                                      FORMAT(1254125.25, 4), `order`.Note FROM `order` LEFT JOIN clients ON `order`.Client_Id = clients.Id
                                      LEFT JOIN clients_actual_address ON `order`.Clients_Adress_Id = clients_actual_address.Id"""
        self.query_table_dell = "DELETE FROM `order` WHERE Id = %s"

    def set_table_header(self):
        i = 0
        self.table_widget.clear()
        for headet_item in self.table_header_name:
            self.table_widget.insertColumn(i)
            self.table_widget.setHorizontalHeaderItem(i, QTableWidgetItem(headet_item[0]))
            self.table_widget.horizontalHeader().resizeSection(i, int(headet_item[1]))
            i += 1

    def set_table_info(self):
        self.table_items = my_sql.sql_select(self.query_table_select)
        if "mysql.connector.errors" in str(type(self.table_items)):
                QMessageBox.critical(self, "Ошибка sql получение таблицы", self.table_items.msg, QMessageBox.Ok)
                return False

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        if not self.table_items:
            return False

        for table_typle in self.table_items:
            self.table_widget.insertRow(self.table_widget.rowCount())
            for column in range(1, len(table_typle)):
                if isinstance(table_typle[column], Decimal):
                    text = re.sub(r'(?<=\d)(?=(\d\d\d)+\b.)', ' ', str(table_typle[column]))
                elif isinstance(table_typle[column], datetime.date):
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
                QMessageBox.critical(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
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

    def ui_dell_table_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить элемент?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                id_item = self.table_widget.selectedItems()
            except:
                QMessageBox.critical(self, "Ошибка Удаления", "Выделите элемент который хотите удалить", QMessageBox.Ok)
                return False
            for id in id_item:
                sql_info = my_sql.sql_change(self.query_table_dell, (id.data(5), ))
                if "mysql.connector.errors" in str(type(sql_info)):
                    QMessageBox.critical(self, "Ошибка sql удаления элемента таблицы", sql_info.msg, QMessageBox.Ok)
                    return False
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