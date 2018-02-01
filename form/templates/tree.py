from os import getcwd
from treelib import Tree
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QMainWindow, QFileDialog, QTreeWidgetItem
from PyQt5.uic import loadUi
from pony.orm import *
from my_class.orm_class import Parts, PartsTree
from my_class import print_qt
from function import to_excel, table_to_html


COLOR_WINDOW = "255, 255, 255"


class TreeList(QMainWindow):
    def __init__(self, main_class=0, dc_select=False, open_id=None):
        super(TreeList, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/tree_table/tree.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.main = main_class
        self.dc_select = dc_select

        self.select_item = open_id  # Переменная для открытия выбраного ID

        self.fast_filter_select = False  # Переменная показывает вызвали ли мы бфстрый фильтр.

        self.set_settings()
        self.set_table_header()
        self.set_tree_info()
        self.set_table_info()
        # if open_id:
        #     self.open_id(self.select_item)

    def set_settings(self):
        self.setWindowTitle("Список")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("1", 100), ("2", 150), ("3", 200))

        self.tree_orm = PartsTree  # Класс дерева!

        # нулевой элемент должен быть ID а первый Parent_ID (ID категории)
        self.item = Parts  # Класс который будем выводить! Без скобок!
        # сам запрос
        self.query = select((p.id, p.tree, p.name, p.note) for p in Parts)

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

    @db_session
    def set_table_info(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

        self.table_items = self.query[:]

        if not self.table_items:
            return False

        for table_typle in self.table_items:
            self.table_widget.insertRow(self.table_widget.rowCount())
            for column in range(2, len(table_typle)):
                item = QTableWidgetItem(str(table_typle[column]))
                item.setData(5, table_typle[0])
                self.table_widget.setItem(self.table_widget.rowCount() - 1, column - 2, item)

        self.table_widget.setSortingEnabled(True)

        if not self.fast_filter_select:
            try:
                item = self.tree_widget.currentItem()
                if item.data(0, 5) >= 0:  # Проверка не выбрано ли показать все!
                    self.ui_sorting(item)
            except:
                pass
        else:
            self.fast_filter_select = False

        if self.select_item:
            self.open_id(self.select_item)
            self.select_item = None

    @db_session
    def set_tree_info(self):  # заполняем девево
        self.tree = Tree()

        all = self.tree_orm.select().order_by(self.tree_orm.parent, self.tree_orm.position)[:]

        self.tree_widget.clear()

        # Создаем дерево в памяти
        self.tree.create_node("main", 0)
        for tree_item in all:
            self.tree.create_node(tree_item.name, tree_item.id, parent=tree_item.parent)
        else:
            self.tree.create_node("Показать всё", "all", parent=0, data="all")

        # Берем созданое дерево и строим его UI обходя все ветви
        for node in self.tree.children(0):
            root_item = self.search(node.identifier)
            self.tree_widget.addTopLevelItem(root_item)

    def search(self, id):  # Ищем ветви дерева
        item = QTreeWidgetItem((self.tree[id].tag, ))  # Создаем полученый Id
        item.setData(0, 5, self.tree[id].identifier)  # Добавляем ID
        for id in self.tree[id].fpointer:  # Смотрим есть ли дети у этой ветви, если есть обзодим их
            item.addChild(self.search(id))  # Добавляем детей этой ветви!

        return item

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
        if tree_id == "all":
            self.set_table_info()
        else:
            self.table_widget.clearContents()
            self.table_widget.setRowCount(0)
            for table_typle in self.table_items:
                if table_typle[1].id == tree_id:
                    self.table_widget.insertRow(self.table_widget.rowCount())
                    for column in range(2, len(table_typle)):
                        item = QTableWidgetItem(str(table_typle[column]))
                        item.setData(5, table_typle[0])
                        self.table_widget.setItem(self.table_widget.rowCount() - 1, column - 2, item)

        self.table_widget.setSortingEnabled(True)

    @db_session
    def ui_add_tree_item(self):
        info = ChangeTreeItem()
        info.set_settings(self.set_new_win_tree)
        if info.exec() == 0:
            return False

        pos = info.le_position.text() or None

        if info.rb_new.isChecked():
            parent_id = 0
        else:
            try:
                parent_id = self.tree_widget.selectedItems()[0].data(0, 5)
            except:
                QMessageBox.critical(self, "Ошибка добавления", "Выделите элемент в который вы хотите вставить элемент", QMessageBox.Ok)
                return False

        self.tree_orm(name=info.le_name.text(), position=pos, parent=parent_id)
        commit()

        self.set_tree_info()

    @db_session
    def ui_change_tree_item(self):

        try:
            parent_name = self.tree_widget.selectedItems()[0].text(0)
            id_select = self.tree_widget.selectedItems()[0].data(0, 5)
        except:
            QMessageBox.critical(self, "Ошибка изменения", "Выделите элемент который хотите изменить", QMessageBox.Ok)
            return False

        tree = self.tree_orm[id_select]

        info = ChangeTreeItem()
        info.set_settings(self.set_new_win_tree)
        info.rb_old.close()
        info.rb_new.close()
        info.le_name.setText(parent_name)
        info.le_position.setText(str(tree.position))
        if info.exec() == 0:
            return False

        tree.name = info.le_name.text()
        tree.position = info.le_position.text() or None
        commit()

        self.set_tree_info()

    @db_session
    def ui_dell_tree_item(self):
        result = QMessageBox.question(self, "Удаление", "Точно удалить ветку?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                if self.tree_widget.selectedItems()[0].childCount() == 0:

                    id_select = self.tree_widget.selectedItems()[0].data(0, 5)
                    self.tree_orm[id_select].delete()
                    commit()
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
            self.main.of_tree_select_operation(item.data(5))
            self.close()
            self.destroy()

    @db_session
    def ui_dell_table_item(self):  # Удалить предмет
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
                QMessageBox.critical(self, "Ошибка Удаления", "Этот элемент используется", QMessageBox.Ok)
                return False
            commit()
            self.set_table_info()
            # self.set_tree_info()

    def ui_filter_table(self):
        pass

    @db_session
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

        info = TreeTransfer(self.tree_orm)
        info.set_settings(self.set_transfer_win)
        if info.exec() == 0:
            return False

        if not info.select_tree_id:
            QMessageBox.critical(self, "Ошибка переноса", "Выберете в каую категорию перенести", QMessageBox.Ok)
        new_tree_id = info.select_tree_id

        for item_id in transfer_id:
            self.item[item_id].tree = new_tree_id
            commit()
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
        self.table_widget.setSortingEnabled(True)

    def ui_update_tree(self):
        self.set_tree_info()

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


class ChangeTreeItem(QDialog):
    def __init__(self):
        super(ChangeTreeItem, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/tree_table/add_tree_item.ui', self)
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


class TreeTransfer(QDialog):
    def __init__(self, orm):
        super(TreeTransfer, self).__init__()
        loadUi(getcwd() + '/ui/templates ui/tree_table/tree_transfer.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.tree_orm = orm
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
        self.tree = Tree()

        all = self.tree_orm.select().order_by(self.tree_orm.parent, desc(self.tree_orm.position))[:]

        self.tree_widget.clear()

        # Создаем дерево в памяти
        self.tree.create_node("main", 0)
        for tree_item in all:
            self.tree.create_node(tree_item.name, tree_item.id, parent=tree_item.parent)

        else:
            self.tree.create_node("Показать всё", "all", parent=0, data="all")

        # Берем главные разделы и начинаем обходить их детей!
        for node in self.tree.children(0):
            root_item = self.search(node.identifier)
            self.tree_widget.addTopLevelItem(root_item)

    def search(self, id):  # Ищем ветви дерева
        item = QTreeWidgetItem((self.tree[id].tag, ))  # Создаем полученый Id
        item.setData(0, 5, self.tree[id].identifier)  # Добавляем ID
        for id in self.tree[id].fpointer:  # Смотрим есть ли дети у этой ветви, если есть обзодим их
            item.addChild(self.search(id))  # Добавляем детей этой ветви!

        return item

    def ui_save_tree_item(self, item):
        self.select_tree_id = item.data(0, 5)
