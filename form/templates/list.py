from os import getcwd
from form.templates import item_2
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from pony.orm import *


class ListItems(QMainWindow):
    def __init__(self, main_class=0, dc_select=False):
        super(ListItems, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/list/list_item.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.m_class = main_class
        self.dc_select = dc_select

        self.set_settings()
        self.sql_set_list()

    def set_settings(self):
        self.setWindowTitle("Список")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(255, 255, 255);")  # Цвет бара
        self.title_new_window = "Предмет"  # Имя вызываемых окон

        self.item = "orm.Country"  # Класс который будем выводить! Без скобок!

        self.set_new_win = {"WinTitle": "Предмет",
                            "WinColor": "(255, 255, 255)",
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    @db_session
    def sql_set_list(self):
        self.lw_list.clear()

        list_items = self.item.select()[:]

        for item in list_items:
            qlist_item = QListWidgetItem(item.name)
            qlist_item.setData(5, item.id)
            self.lw_list.addItem(qlist_item)

    @db_session
    def ui_add_item(self):
        add_item_window = item_2.Item2()
        add_item_window.set_settings(self.set_new_win)
        add_item_window.setModal(True)
        add_item_window.show()
        if add_item_window.exec() == 0:
            return False

        self.item(name = add_item_window.le_name.text(), note = add_item_window.pe_note.toPlainText())

        self.sql_set_list()

    @db_session
    def ui_change_item(self, sel_id=False):
        if sel_id:
            select_id = sel_id
        else:
            try:
                select_id = self.lw_list.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка", "Выберете элемент", QMessageBox.Ok)
                return False

        select_item_class = self.item[int(select_id)]
        commit()

        change_item_window = item_2.Item2()
        change_item_window.set_settings(self.set_new_win)
        change_item_window.le_name.setText(select_item_class.name)
        change_item_window.pe_note.appendPlainText(select_item_class.note)
        change_item_window.setModal(True)
        change_item_window.show()
        if change_item_window.exec() == 0:
            return False

        select_item_class.name = change_item_window.le_name.text()
        select_item_class.note = change_item_window.pe_note.toPlainText()

        self.sql_set_list()

    @db_session
    def ui_dell_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить элемент?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                id_select = self.lw_list.selectedItems()[0].data(5)
                self.item[int(id_select)].delete()
                self.sql_set_list()
            except:
                QMessageBox.critical(self, "Ошибка", "Выберете элемент", QMessageBox.Ok)

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select(select_prov.data(5))
            self.close()
            self.destroy()
