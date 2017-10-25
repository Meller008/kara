from os import getcwd
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QMainWindow, QTreeWidgetItem, QFileDialog
from PyQt5.uic import loadUiType
from classes import print_qt
from classes.my_class import User
from function import to_excel, my_sql, table_to_html

tree_class = loadUiType(getcwd() + '/ui/templates ui/tree.ui')[0]
change_tree_item_class = loadUiType(getcwd() + '/ui/templates ui/add_tree_item.ui')[0]
transfer_class = loadUiType(getcwd() + '/ui/templates ui/tree_transfer.ui')[0]


class TreeList(QMainWindow, tree_class):
    def __init__(self, main_class=0, dc_select=False, open_id=None):
        super(TreeList, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.main = main_class
        self.dc_select = dc_select

        self.select_item = open_id  # Переменная для открытия выбраного ID

        self.access()
        self.set_settings()
        self.set_table_header()
        self.set_tree_info()
        self.set_table_info()
        # if open_id:
        #     self.open_id(self.select_item)

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

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("1", 100), ("2", 150), ("3", 200))

        self.query_tree_select = "SELECT Id, Parent_Id, Name FROM operation_tree"
        self.query_tree_add = "INSERT INTO operation_tree (Parent_Id, Name) VALUES (%s, %s)"
        self.query_tree_change = "UPDATE operation_tree SET Name = %s WHERE Id = %s"
        self.query_tree_del = "DELETE FROM operation_tree WHERE Id = %s"

        #  нулевой элемент должен быть ID а первый Parent_ID (ID категории)
        self.query_table_select = "SELECT operations.Id, operations.Tree_Id, operations.Name, operations.Price, sewing_machine.Name  " \
                                  "FROM operations LEFT JOIN sewing_machine ON operations.Sewing_Machine_Id = sewing_machine.Id"
        self.query_transfer_item = "UPDATE operations SET Tree_Id = %s WHERE Id = %s"
        self.query_table_dell = "DELETE FROM operations WHERE Id = %s"

        # Настройки окна добавления и редактирования дерева
        self.set_new_win_tree = {"WinTitle": "Добавление категории",
                                 "WinColor": "(255, 255, 255)",
                                 "lb_name": "Название категории"}

        # Настройки окна переноса элементов
        self.set_transfer_win = {"WinTitle": "Изменение категории",
                                 "WinColor": "(255, 255, 255)"}

    def set_table_header(self):
        i = 0
        self.table_widget.clear()
        for headet_item in self.table_header_name:
            self.table_widget.insertColumn(i)
            self.table_widget.setHorizontalHeaderItem(i, QTableWidgetItem(headet_item[0]))
            self.table_widget.horizontalHeader().resizeSection(i, int(headet_item[1]))
            i += 1

    def set_table_info(self):
        self.table_widget.setSortingEnabled(False)
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
            for column in range(2, len(table_typle)):
                item = QTableWidgetItem(str(table_typle[column]))
                item.setData(5, table_typle[0])
                self.table_widget.setItem(self.table_widget.rowCount() - 1, column - 2, item)

        self.table_widget.setSortingEnabled(True)

        try:
            item = self.tree_widget.currentItem()
            if item.data(0, 5) >= 0:  # Проверка не выбрано ли показать все!
                self.ui_sorting(item)
        except:
            pass

        if self.select_item:
            self.open_id(self.select_item)
            self.select_item = None

    def set_tree_info(self):  # заполняем девево
        self.tree = my_sql.sql_select(self.query_tree_select)
        if "mysql.connector.errors" in str(type(self.tree)):
            QMessageBox.critical(self, "Ошибка sql вывода дерева", self.tree.msg, QMessageBox.Ok)
            return False

        self.tree_widget.clear()
        # i = 0
        # while self.tree and i < 10:
        for item_tree in self.tree:
            if item_tree[1] == 0:
                add_item = QTreeWidgetItem((item_tree[2], ))
                add_item.setData(0, 5, item_tree[0])
                self.tree_widget.addTopLevelItem(add_item)
            else:
                for n in range(self.tree_widget.topLevelItemCount()):
                    item = self.tree_widget.topLevelItem(n)
                    self.search(item, item_tree)

        add_item = QTreeWidgetItem(("Показать всё", ))
        add_item.setData(0, 5, -1)
        self.tree_widget.addTopLevelItem(add_item)

    def search(self, item, search_tuple):  # Ищет кортеж в детях главных итемах дерева
        if item.data(0, 5) == search_tuple[1]:
            add_item = QTreeWidgetItem((search_tuple[2], ))
            add_item.setData(0, 5, search_tuple[0])
            item.addChild(add_item)
            return True
        else:
            for number_child in range(item.childCount()):
                self.search(item.child(number_child), search_tuple)
            return False

    def open_id(self, id):
        select_item = None
        for item in self.table_items:
            if item[0] == id:
                select_item = item
                break

        if not select_item:
            return False

        open_dir_id = []
        search_tree_id = select_item[1]

        def search(id):
            for tree_item in self.tree:
                if tree_item[0] == id:
                    if tree_item[1] == 0:
                        open_dir_id.append(tree_item[0])
                        return True
                    else:
                        open_dir_id.append(tree_item[0])
                        search(tree_item[1])
                        return True

        search(search_tree_id)

        def search_tree_widget(search_tree_item):
            t_item = None
            for level in range(search_tree_item.childCount()):
                t_item = search_tree_item.child(level)
                if t_item.data(0, 5) in open_dir_id:
                    self.tree_widget.expandItem(t_item)
                    open_dir_id.remove(t_item.data(0, 5))
                    break

            if not tree_item:
                return False

            if tree_item.childCount() > 0 and open_dir_id:
                search_tree_widget(t_item)
                return True
            else:
                self.tree_widget.setCurrentItem(t_item)
                return True

        tree_item = None
        for level_tree in range(self.tree_widget.topLevelItemCount()):
            tree_item = self.tree_widget.topLevelItem(level_tree)
            if tree_item.data(0, 5) in open_dir_id:
                self.tree_widget.expandItem(tree_item)
                open_dir_id.remove(tree_item.data(0, 5))
                break

        if not tree_item:
            return False

        if tree_item.childCount() > 0 and open_dir_id:
            search_tree_widget(tree_item)
        else:
            self.tree_widget.setCurrentItem(tree_item)

        self.ui_sorting(self.tree_widget.currentItem())

        for row in range(self.table_widget.rowCount()):
            if self.table_widget.item(row, 0).data(5) == id:
                self.table_widget.setCurrentCell(row, self.table_widget.columnCount()-1)
                self.table_widget.setFocus()
                break

        return True

    def ui_sorting(self, select_tree):
        tree_id = select_tree.data(0, 5)
        if not self.table_items:
            return False

        self.table_widget.setSortingEnabled(False)
        if tree_id == -1:
            self.set_table_info()
        else:
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            for table_typle in self.table_items:
                if table_typle[1] == tree_id:
                    self.table_widget.insertRow(self.table_widget.rowCount())
                    for column in range(2, len(table_typle)):
                        item = QTableWidgetItem(str(table_typle[column]))
                        item.setData(5, table_typle[0])
                        self.table_widget.setItem(self.table_widget.rowCount() - 1, column - 2, item)

        self.table_widget.setSortingEnabled(True)

    def ui_add_tree_item(self):
        info = ChangeTreeItem()
        info.set_settings(self.set_new_win_tree)
        if info.exec() == 0:
            return False
        if info.rb_new.isChecked():
            sql_tree =  my_sql.sql_change(self.query_tree_add, (0, info.le_name.text(), info.le_position.text()))
            if "mysql.connector.errors" in str(type(sql_tree)):
                QMessageBox.critical(self, "Ошибка sql добавления корневого итема в дерево", sql_tree.msg, QMessageBox.Ok)
                return False
            self.set_tree_info()
        elif info.rb_old.isChecked():
            try:
                parent_id = self.tree_widget.selectedItems()[0].data(0, 5)
                sql_tree = my_sql.sql_change(self.query_tree_add, (parent_id, info.le_name.text(), info.le_position.text()))
                if "mysql.connector.errors" in str(type(sql_tree)):
                    QMessageBox.critical(self, "Ошибка sql добавления итема в дерево", sql_tree.msg, QMessageBox.Ok)
                    return False
                self.set_tree_info()
            except:
                  QMessageBox.critical(self, "Ошибка добавления", "Выделите элемент в который вы хотите вставить элемент", QMessageBox.Ok)

    def ui_change_tree_item(self):

        try:
            parent_name = self.tree_widget.selectedItems()[0].text(0)
            parent_id = self.tree_widget.selectedItems()[0].data(0, 5)
            info = ChangeTreeItem()
            info.set_settings(self.set_new_win_tree)
            info.rb_old.close()
            info.rb_new.close()
            info.le_name.setText(parent_name)
            if info.exec() == 0:
                return False
            sql_tree = my_sql.sql_change(self.query_tree_change, (info.le_name.text(), info.le_position.text(), parent_id))
            if "mysql.connector.errors" in str(type(sql_tree)):
                QMessageBox.critical(self, "Ошибка sql изменения итема в дереве", sql_tree.msg, QMessageBox.Ok)
                return False
            self.set_tree_info()
        except:
            QMessageBox.critical(self, "Ошибка изменения", "Выделите элемент который хотите изменить", QMessageBox.Ok)

    def ui_dell_tree_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить ветку?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                parent_id = self.tree_widget.selectedItems()[0].data(0, 5)
                if self.tree_widget.selectedItems()[0].childCount() == 0:
                    sql_tree = my_sql.sql_change(self.query_tree_del, (parent_id, ))
                    if "mysql.connector.errors" in str(type(sql_tree)):
                        QMessageBox.critical(self, "Ошибка sql удаления итема в дереве", sql_tree.msg, QMessageBox.Ok)
                        return False
                    self.set_tree_info()
                else:
                    QMessageBox.critical(self, "Ошибка", "У этого элеиента есть дети удалите сначало их", QMessageBox.Ok)
            except:
                QMessageBox.critical(self, "Ошибка ", "Выделите элемент который хотите удалить", QMessageBox.Ok)
                return False

    def ui_add_table_item(self):  # Добавить предмет
        try:
            tree_id = self.tree_widget.selectedItems()[0].data(0, 5)
        except:
            QMessageBox.critical(self, "Ошибка ", "Выделите элемент дерева куда добавлять предмет", QMessageBox.Ok)
            return False
        if tree_id < 0:
            QMessageBox.critical(self, "Ошибка ", "Вы выбрали неправильный элемент", QMessageBox.Ok)
            return False

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

    def ui_dell_table_item(self):  # Удалить предмет
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
            # self.set_tree_info()

    def ui_filter_table(self):
        pass

    def ui_transfer_table(self):
        try:
            transfer_id = []
            for item in self.table_widget.selectedItems():
                if item.data(5) not in transfer_id:
                 transfer_id.append(item.data(5))
        except:
            QMessageBox.critical(self, "Ошибка переноса", "Выберете элементы для переноса", QMessageBox.Ok)
            return False
        if not transfer_id:
            QMessageBox.critical(self, "Ошибка переноса", "Выберете элементы для переноса", QMessageBox.Ok)
            return False

        info = TreeTransfer(self.query_tree_select)
        info.set_settings(self.set_transfer_win)
        if info.exec() == 0:
            return False

        if not info.select_tree_id:
            QMessageBox.critical(self, "Ошибка переноса", "Выберете в каую категорию перенести", QMessageBox.Ok)
        new_tree_id = info.select_tree_id

        for item_id in transfer_id:
            sql_info = my_sql.sql_change(self.query_transfer_item, (new_tree_id, item_id))
            if "mysql.connector.errors" in str(type(sql_info)):
                QMessageBox.critical(self, "Ошибка sql получение табюлицы", sql_info.msg, QMessageBox.Ok)
                return False
        self.set_table_info()

    def ui_double_item_table(self):  # Дублирование строки
        if id:
            item_id = id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.critical(self, "Ошибка ", "Выделите элемент который хотите дублировать", QMessageBox.Ok)
                return False

        pass

    def ui_update_table(self):
        self.table_widget.setSortingEnabled(False)
        self.set_table_info()
        self.set_tree_info()
        self.table_widget.setSortingEnabled(True)

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


class ChangeTreeItem(QDialog, change_tree_item_class):
    def __init__(self):
        super(ChangeTreeItem, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

    def set_settings(self, setting):
        self.collor = (252, 163, 255)
        for name, value in setting.items():
            if name == "WinTitle":
                self.setWindowTitle(value)
            elif name == "WinColor":
                self.widget.setStyleSheet("background-color: rgb%s;" % value)
            else:
                getattr(self, name).setText(value)


class TreeTransfer(QDialog, transfer_class):
    def __init__(self, query):
        super(TreeTransfer, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.query_tree_select = query
        self.set_tree_info()
        self.select_tree_id = False

    def set_settings(self, setting):
        self.collor = (252, 163, 255)
        for name, value in setting.items():
            if name == "WinTitle":
                self.setWindowTitle(value)
            elif name == "WinColor":
                self.widget.setStyleSheet("background-color: rgb%s;" % value)
            else:
                getattr(self, name).setText(value)

    def set_tree_info(self):  # заполняем девево
        self.tree = my_sql.sql_select(self.query_tree_select)
        if "mysql.connector.errors" in str(type(self.tree)):
            QMessageBox.critical(self, "Ошибка sql вывода дерева", self.tree.msg, QMessageBox.Ok)
            return False

        self.tree_widget.clear()
        for item_tree in self.tree:
            if item_tree[1] == 0:
                add_item = QTreeWidgetItem((item_tree[2], ))
                add_item.setData(0, 5, item_tree[0])
                self.tree_widget.addTopLevelItem(add_item)
            else:
                for n in range(self.tree_widget.topLevelItemCount()):
                    item = self.tree_widget.topLevelItem(n)
                    self.search(item, item_tree)

    def search(self, item, search_tuple):  # Ищет кортеж в детях главных итемах дерева
        if item.data(0, 5) == search_tuple[1]:
            add_item = QTreeWidgetItem((search_tuple[2], ))
            add_item.setData(0, 5, search_tuple[0])
            item.addChild(add_item)
            self.tree.remove(search_tuple)
            return True
        else:
            for number_child in range(item.childCount()):
                self.search(item.child(number_child), search_tuple)
            return False

    def ui_save_tree_item(self, item):
        self.select_tree_id = item.data(0, 5)
