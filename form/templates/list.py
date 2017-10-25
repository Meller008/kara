from os import getcwd
from form.templates import item_2
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QMessageBox, QListWidgetItem, QMainWindow
from PyQt5.QtGui import QIcon
from function import my_sql
from classes.my_class import User

list_class = loadUiType(getcwd() + '/ui/templates ui/list_item.ui')[0]


class ListItems(QMainWindow, list_class):
    def __init__(self, main_class=0, dc_select=False):
        super(ListItems, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.set_settings()
        self.sql_set_list()
        self.m_class = main_class
        self.dc_select = dc_select
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
                    val = item["value"]
                a(val)
            else:
                a()

    def set_settings(self):
        self.setWindowTitle("Список")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(255, 255, 255);")  # Цвет бара
        self.title_new_window = "Предмет"  # Имя вызываемых окон

        self.sql_list = "Получаем ID + Название"
        self.sql_add = "Вставляем Имя + Заметку"
        self.sql_change_select = "Получаем Имя + заметку через ID"
        self.sql_update_select = 'Меняем Имя + заметку через ID'
        self.sql_dell = "Удаляем строку через ID"

        self.set_new_win = {"WinTitle": "Предмет",
                            "WinColor": "(255, 255, 255)",
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def sql_set_list(self):
        sql_result = my_sql.sql_select(self.sql_list)
        if "mysql.connector.errors" in str(type(sql_result)):
            QMessageBox.critical(self, "Ошибка sql вывода списка", sql_result.msg, QMessageBox.Ok)
            return False
        else:
            self.lw_list.clear()
            for item in sql_result:
                item_list = QListWidgetItem(item[1])
                item_list.setData(3, item[0])
                self.lw_list.addItem(item_list)

    def ui_add_item(self):
        add_item = item_2.Item2()
        add_item.set_settings(self.set_new_win)
        add_item.setModal(True)
        add_item.show()
        if add_item.exec() == 0:
            return False
        sql_result = my_sql.sql_change(self.sql_add, (add_item.le_name.text(), add_item.pe_note.toPlainText()))
        if "mysql.connector.errors" in str(type(sql_result)):
            QMessageBox.critical(self, "Ошибка sql добавление предмета", sql_result.msg, QMessageBox.Ok)
            return False
        self.sql_set_list()

    def ui_change_item(self, id=False):
        if id:
            id_select = id
        else:
            try:
                id_select = self.lw_list.selectedItems()[0].data(3)
            except:
                QMessageBox.critical(self, "Ошибка", "Выберете элемент", QMessageBox.Ok)
                return False

        sql_result = my_sql.sql_select(self.sql_change_select, (id_select, ))
        if "mysql.connector.errors" in str(type(sql_result)):
            QMessageBox.critical(self, "Ошибка sql получение предмета", sql_result.msg, QMessageBox.Ok)
            return False
        change_item = item_2.Item2()
        change_item.set_settings(self.set_new_win)
        change_item.le_name.setText(sql_result[0][0])
        change_item.pe_note.appendPlainText(sql_result[0][1])
        change_item.setModal(True)
        change_item.show()
        if change_item.exec() == 0:
            return False
        sql_result = my_sql.sql_change(self.sql_update_select, (change_item.le_name.text(), change_item.pe_note.toPlainText(), id_select))
        if "mysql.connector.errors" in str(type(sql_result)):
            QMessageBox.critical(self, "Ошибка sql добавление предмета", sql_result.msg, QMessageBox.Ok)
            return False
        self.sql_set_list()

    def ui_dell_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить элемент?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                id_select = self.lw_list.selectedItems()[0].data(3)
                sql_result = my_sql.sql_change(self.sql_dell, (id_select, ))
                if "mysql.connector.errors" in str(type(sql_result)):
                    QMessageBox.critical(self, "Ошибка sql удаление предмета", sql_result.msg, QMessageBox.Ok)
                    return False
                self.sql_set_list()
            except:
                QMessageBox.critical(self, "Ошибка", "Выберете элемент", QMessageBox.Ok)

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(3))
        else:
            item = (select_prov.data(3), select_prov.text())
            self.m_class.of_list_insert(item)
            self.close()
            self.destroy()
