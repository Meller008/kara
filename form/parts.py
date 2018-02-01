from os import getcwd, path, mkdir, remove
import shutil
from urllib.request import urlretrieve
from treelib import Tree
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem, QTreeWidgetItem, QListWidgetItem, QInputDialog, QLineEdit, QWidget, QSizePolicy
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt
from pony.orm import *
from my_class.orm_class import Parts, PartsTree, ManufacturerParts, SewingMachine, TypeSewingMachine, ManufacturerSewingMachine, \
    SupplyPosition
from form import sewing_machine
from form.templates import tree, list
from function.str_to import str_to_float

COLOR_WINDOW_PARTS = "0, 102, 102"
COLOR_WINDOW_PARTS_MANUFACTURER = "204, 255, 255"
PHOTO_DIR = getcwd() + "/photo/"

db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class PartsList(tree.TreeList):
    def set_settings(self):
        self.setWindowTitle("Список товара")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS)  # Цвет бара

        self.pb_other.deleteLater()
        self.pb_table_double.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Артикул", 60), ("Имя", 150), ("Цена", 60), ("Заметка", 250))

        self.tree_orm = PartsTree  # Класс дерева!

        # нулевой элемент должен быть ID а первый Parent_ID (ID категории)
        self.item = Parts  # Класс который будем выводить! Без скобок!
        # сам запрос
        self.query_all = select((p.id, p.tree, p.id, p.name, p.price, p.note) for p in Parts)
        self.query = self.query_all

        # Настройки окна добавления и редактирования дерева
        self.set_new_win_tree = {"WinTitle": "Добавление категории",
                                 "WinColor": "(255, 255, 255)",
                                 "lb_name": "Название категории"}

        # Настройки окна переноса элементов
        self.set_transfer_win = {"WinTitle": "Изменение категории",
                                 "WinColor": "(255, 255, 255)"}

        # Быстрый фильтр
        self.le_fast_filter = QLineEdit()
        self.le_fast_filter.setPlaceholderText("Артикул")
        self.le_fast_filter.setMaximumWidth(150)
        self.le_fast_filter.editingFinished.connect(self.fast_filter)
        dummy = QWidget()
        dummy.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.toolBar.addWidget(dummy)
        self.toolBar.addWidget(self.le_fast_filter)

    def ui_add_table_item(self):  # Добавить предмет
        try:
            tree_id = self.tree_widget.selectedItems()[0].data(0, 5)
        except:
            QMessageBox.critical(self, "Ошибка ", "Выделите элемент дерева куда добавлять предмет", QMessageBox.Ok)
            return False
        if tree_id == 'all':
            QMessageBox.critical(self, "Ошибка ", "Вы выбрали неправильный элемент", QMessageBox.Ok)
            return False

        self.add_parts = PartsWindow(self, tree_id=tree_id)
        self.add_parts.setWindowModality(Qt.ApplicationModal)
        self.add_parts.show()

    def ui_change_table_item(self, id=False):  # изменить элемент
        if id:
            item_id = id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.critical(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
                return False

        self.change_parts = PartsWindow(self, product_id=item_id)
        self.change_parts.setWindowModality(Qt.ApplicationModal)
        self.change_parts.show()

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            self.main.of_tree_select_product(item.data(5))
            self.close()
            self.destroy()

    def fast_filter(self):
        # Блок условий артикула
        if self.le_fast_filter.text() != '':
            text = self.le_fast_filter.text()
            self.query = self.query_all.where(lambda p: text in p.name or text == p.id)
            self.fast_filter_select = True
        else:
            self.query = self.query_all

        self.ui_update_table()


class PartsWindow(QMainWindow):
    def __init__(self, main=None, product_id=None, tree_id=None):
        super(PartsWindow, self).__init__()
        loadUi(getcwd() + '/ui/product.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS)

        self.main = main
        self.id = product_id
        self.tree_id = tree_id

        self.photo_dir = ""
        self.photo_del = False

        self.machine_id_new = []
        self.machine_id_del = []

        self.start()

    @db_session
    def start(self):
        if self.id:
            product = Parts[self.id]
            self.le_article.setText(str(product.id))
            self.le_name.setText(product.name)
            self.le_vaendor_name.setText(product.vendor_name)
            self.le_note.setText(product.note)
            self.le_manufacturer.setText(product.manufacturer.name)
            self.le_manufacturer.setWhatsThis(str(product.manufacturer.id))
            self.le_price.setText(str(product.price))

            for machine in product.sewing_machines:
                self.tw_machine.insertRow(self.tw_machine.rowCount())

                item = QTableWidgetItem(machine.name)
                item.setData(5, machine.id)
                self.tw_machine.setItem(self.tw_machine.rowCount() - 1, 0, item)

                item = QTableWidgetItem(machine.manufacturer.name)
                item.setData(5, machine.id)
                self.tw_machine.setItem(self.tw_machine.rowCount() - 1, 1, item)

            path_photo = self.inspection_path(product.id)
            img = QImage(path_photo + "/main.jpg")
            img = img.scaled(self.lb_photo.height(), self.lb_photo.width(), Qt.KeepAspectRatio)
            self.lb_photo.setPixmap(QPixmap().fromImage(img))

        else:
            self.le_article.setText("new")

        self.tw_machine.horizontalHeader().resizeSection(0, 150)
        self.tw_machine.horizontalHeader().resizeSection(1, 150)

    def inspection_path(self, dir_name):  # Находим путь работника
        if not path.isdir("%s/%s" % (PHOTO_DIR, dir_name)):
            try:
                mkdir("%s/%s" % (PHOTO_DIR, dir_name))
                return "%s/%s" % (PHOTO_DIR, dir_name)
            except:
                QMessageBox.critical(self, "Ошибка файлы", "Нет доступа к корневому диалогу, файлы недоступны", QMessageBox.Ok)
                return False
        else:
            return "%s/%s" % (PHOTO_DIR, dir_name)

    def ui_view_manufacturer(self):
        self.manufacturer_parts = PartsManufacturer(self, True)
        self.manufacturer_parts.setWindowModality(Qt.ApplicationModal)
        self.manufacturer_parts.show()

    def ui_web_photo(self):
        url = QInputDialog.getText(self, "Введите URL фото", "URL")[0]

        if url:
            path_photo = self.inspection_path(self.id) + "/main.jpg"
            if path.isfile(path_photo):
                remove(path_photo)

            try:
                urlretrieve(url, path_photo)
            except ValueError:
                QMessageBox.information(self, "Ошибка url", "unknown url type", QMessageBox.Ok)
                return False

            img = QImage(path_photo)
            img = img.scaled(self.lb_photo.height(), self.lb_photo.width(), Qt.KeepAspectRatio)
            self.lb_photo.setPixmap(QPixmap().fromImage(img))

            self.photo_dir = path_photo
            self.photo_del = False

    def ui_change_photo(self):
        dir = QFileDialog.getOpenFileNames(self, "Выбор фото", "", "*.jpg")[0]
        if not dir:
            return False

        img = QImage(dir[0])
        img = img.scaled(self.lb_photo.height(), self.lb_photo.width(), Qt.KeepAspectRatio)
        self.lb_photo.setPixmap(QPixmap().fromImage(img))

        self.photo_dir = dir[0]
        self.photo_del = False

    def ui_del_photo(self):
        self.lb_photo.clear()
        self.lb_photo.setText("Фото")
        self.photo_dir = ""
        self.photo_del = True

    def ui_view_machine(self):
        self.machine = sewing_machine.SewingMachineList(self, True)
        self.machine.setWindowModality(Qt.ApplicationModal)
        self.machine.show()

    def ui_del_machine(self):
        row = self.tw_machine.currentRow()
        if row < 0:
            QMessageBox.information(self, "Ошибка ", "Выделите оборудование которое надо удалить", QMessageBox.Ok)
            return False

        try:
            self.machine_id_del.append(self.tw_machine.item(row, 0).data(5))
            self.machine_id_new.remove(self.tw_machine.item(row, 0).data(5))
        except ValueError:
            pass

        self.tw_machine.removeRow(row)

    def ui_copy(self):  # Скопировать данные другой запчасти
        self.parts_list = PartsList(self, True)
        self.parts_list.setWindowModality(Qt.ApplicationModal)
        self.parts_list.show()

    @db_session
    def ui_acc(self):

        value = {
                "name": self.le_name.text(),
                "vendor_name": self.le_vaendor_name.text(),
                "note": self.le_note.text(),
                "manufacturer": self.le_manufacturer.whatsThis(),
                "tree": self.tree_id,
                "price": str_to_float(self.le_price.text())
                }

        if not value["name"] or not value["manufacturer"]:
            QMessageBox.information(self, "Ошибка сохранения", "Не все заполнено", QMessageBox.Ok)
            return False

        if self.id:
            p = Parts[self.id]
            value.pop("tree")
            p.set(**value)
        else:
            p = Parts(**value)

        p.sewing_machines.remove(map(lambda x: SewingMachine[x], self.machine_id_del))
        p.sewing_machines.add(map(lambda x: SewingMachine[x], self.machine_id_new))

        flush()

        if self.photo_del or self.photo_dir:
            path_photo = self.inspection_path(p.id)
            if path_photo:
                if self.photo_del:
                    path_photo += "/main.jpg"
                    remove(path_photo)

                if self.photo_dir:
                    path_photo += "/main.jpg"
                    if self.photo_dir != path_photo:
                        shutil.copy2(self.photo_dir, path_photo)

        self.main.ui_update_table()
        self.close()
        self.destroy()

    def ui_can(self):
        self.destroy()
        self.close()

    @db_session
    def of_list_select_manufacturer_parts(self, id_manuf):
        type = ManufacturerParts[id_manuf]
        self.le_manufacturer.setText(type.name)
        self.le_manufacturer.setWhatsThis(str(type.id))

    @db_session
    def of_select_sewing_machine(self, id_machine):
        machine = SewingMachine[id_machine]

        self.tw_machine.insertRow(self.tw_machine.rowCount())

        item = QTableWidgetItem(machine.name)
        item.setData(5, id_machine)
        self.tw_machine.setItem(self.tw_machine.rowCount() - 1, 0, item)

        item = QTableWidgetItem(machine.manufacturer.name)
        item.setData(5, id_machine)
        self.tw_machine.setItem(self.tw_machine.rowCount() - 1, 1, item)

        try:
            self.machine_id_new.append(id_machine)
            self.machine_id_del.remove(id_machine)
        except ValueError:
            pass

    @db_session
    def of_tree_select_product(self, part_id):  # Вставка скопированой запчасти
        part_copy = Parts[part_id]

        self.le_name.setText(part_copy.name)
        self.le_vaendor_name.setText(part_copy.vendor_name)
        self.le_note.setText(part_copy.note)
        self.le_manufacturer.setText(part_copy.manufacturer.name)
        self.le_manufacturer.setWhatsThis(str(part_copy.manufacturer.id))
        self.le_price.setText(str(part_copy.price))

        for machine in part_copy.sewing_machines:
            self.of_select_sewing_machine(machine.id)

        path_photo = self.inspection_path(part_copy.id)
        img = QImage(path_photo + "/main.jpg")
        img = img.scaled(self.lb_photo.height(), self.lb_photo.width(), Qt.KeepAspectRatio)
        self.lb_photo.setPixmap(QPixmap().fromImage(img))

        self.photo_dir = path_photo + "/main.jpg"
        self.photo_del = False


class PartsManufacturer(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Производители запчастей")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS_MANUFACTURER)  # Цвет бара

        self.item = ManufacturerParts

        self.set_new_win = {"WinTitle": "Производитель",
                            "WinColor": "(%s)" % COLOR_WINDOW_PARTS_MANUFACTURER,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_manufacturer_parts(select_prov.data(5))
            self.close()
            self.destroy()


class PartsCatalog(QMainWindow):
    def __init__(self, main=None):
        super(PartsCatalog, self).__init__()
        loadUi(getcwd() + '/ui/product_catalog.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        # self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS)

        self.main = main

        self.filter_article = None  # Фильтр по артикулу
        self.filter_name = None  # Фильтр по именитовара
        self.filter_manufacturer_name = None  # Фильтр по имени производителя
        self.filter_type_product_id = None  # Фильтр по каталогу продукта
        self.filter_manufacturer_product_id = None  # Фильтр по производителю запчасти
        self.filter_machine_id = None  # Фильтр по ID оборудования
        self.filter_machine_type_id = None  # Фильтр по типу оборудования
        self.filter_machine_man_id = None  # Фильтр по производителю оборудования

        self.start()

    @db_session
    def start(self):
        self.tw_machine.horizontalHeader().resizeSection(0, 50)
        self.tw_machine.horizontalHeader().resizeSection(1, 50)
        self.tw_machine.horizontalHeader().resizeSection(2, 115)

        self.tw_poduct.horizontalHeader().resizeSection(0, 50)
        self.tw_poduct.horizontalHeader().resizeSection(1, 150)
        self.tw_poduct.horizontalHeader().resizeSection(2, 60)
        self.tw_poduct.horizontalHeader().resizeSection(3, 60)
        self.tw_poduct.horizontalHeader().resizeSection(4, 185)


        # Получим дерево товаров
        self.tree_parts = Tree()
        self.tw_tree_product.clear()

        # Создаем дерево в памяти
        self.tree_parts.create_node("main", 0)
        for tree_item in PartsTree.select().order_by(PartsTree.parent, PartsTree.position)[:]:
            self.tree_parts.create_node(tree_item.name, tree_item.id, parent=tree_item.parent)
        else:
            self.tree_parts.create_node("Показать всё", "all", parent=0, data="all")

        # Берем созданое дерево и строим QTreeWidgetItem обходя все ветви
        for node in self.tree_parts.children(0):
            root_item = self.search(node.identifier, self.tree_parts)
            self.tw_tree_product.addTopLevelItem(root_item)

        # Получим производителей З/Ч
        self.lw_manufacturer_parts.clear()
        for manuf in ManufacturerParts.select().order_by(ManufacturerParts.name)[:]:
            item = QListWidgetItem(manuf.name)
            item.setData(5, manuf.id)
            self.lw_manufacturer_parts.addItem(item)
        else:
            item = QListWidgetItem("Все")
            item.setData(5, None)
            self.lw_manufacturer_parts.addItem(item)

        # Получим производителей оборудования
        self.lw_manufacturer_machine.clear()
        for manuf in ManufacturerSewingMachine.select().order_by(ManufacturerSewingMachine.name)[:]:
            item = QListWidgetItem(manuf.name)
            item.setData(5, manuf.id)
            self.lw_manufacturer_machine.addItem(item)
        else:
            item = QListWidgetItem("Все")
            item.setData(5, None)
            self.lw_manufacturer_machine.addItem(item)

        # Получим тип оборудования
        self.lw_type_machine.clear()
        for type in TypeSewingMachine.select().order_by(TypeSewingMachine.name)[:]:
            item = QListWidgetItem(type.name)
            item.setData(5, type.id)
            self.lw_type_machine.addItem(item)
        else:
            item = QListWidgetItem("Все")
            item.setData(5, None)
            self.lw_type_machine.addItem(item)

        self.filter_machine()  # Получим все машины так как фильтра нет

    def ui_change_article(self, text):
        try:
            self.filter_article = int(text)
            self.filter_product()
        except ValueError:
            self.filter_article = None

    def ui_change_name(self, text):
        try:
            self.filter_name = text
            self.filter_product()
        except ValueError:
            self.filter_name = None

    def ui_change_manufacturer_name(self, text):
        try:
            self.filter_manufacturer_name = int(text)
            self.filter_product()
        except ValueError:
            self.filter_manufacturer_name = None

    def ui_change_product_type(self, item):
        _id = item.data(0, 5)

        if _id == 'all':
            _id = None
        else:
            _id = int(_id)

        self.filter_type_product_id = _id

        self.filter_product()

    def ui_change_product_manufacturer_id(self, item):  # Применяем фильтр по производителю продукта
        _id = item.data(5)

        if _id is not None:
            _id = int(_id)

        self.filter_manufacturer_product_id = _id

        self.filter_product()

    def ui_change_machine_id(self, item):  # Вставляем выбраное оборудование в фильтр
        _id = item.data(5)

        if _id is not None:
            _id = int(_id)

        self.filter_machine_id = _id
        self.filter_product()

    def ui_change_manufacturer_machine(self, item):  # применяем фильтр по производителю оборудования
        _id = item.data(5)

        if _id is not None:
            _id = int(_id)

        self.filter_machine_id = None
        self.filter_machine_man_id = _id

        self.filter_machine()
        self.filter_product()

    def ui_change_type_machine(self, item):  # Применяем фильтр по типу оборудования
        _id = item.data(5)

        if _id is not None:
            _id = int(_id)

        self.filter_machine_id = None
        self.filter_machine_type_id = _id

        self.filter_machine()
        self.filter_product()

    def ui_dc_warehouse(self, item):
        if self.main:
            self.main.of_tree_select_catalog_warehouse(item.data(5))
            self.close()
            self.destroy()

    @db_session
    def ui_set_product(self, select_item):  # Отобразим товар
        _id = select_item.data(5)

        self.tw_product_machine.setRowCount(0)
        self.tw_product_machine.clearContents()

        self.tw_product_warehouse.setRowCount(0)
        self.tw_product_warehouse.clearContents()

        product = Parts[int(_id)]

        self.le_article.setText(str(product.id))
        self.le_name.setText(str(product.name))
        self.le_manufacturer_name.setText(str(product.vendor_name))
        self.le_price.setText(str(product.price))
        self.le_manufacturer.setText(str(product.manufacturer.name))
        self.le_note.setText(str(product.note))

        for machine in product.sewing_machines:
                self.tw_product_machine.insertRow(self.tw_product_machine.rowCount())

                item = QTableWidgetItem(machine.name)
                item.setData(5, machine.id)
                self.tw_product_machine.setItem(self.tw_product_machine.rowCount() - 1, 0, item)

                item = QTableWidgetItem(machine.manufacturer.name)
                item.setData(5, machine.id)
                self.tw_product_machine.setItem(self.tw_product_machine.rowCount() - 1, 1, item)

        path_photo = self.inspection_path(product.id)
        img = QImage(path_photo + "/main.jpg")
        img = img.scaled(self.lb_phot.height(), self.lb_phot.width(), Qt.KeepAspectRatio)
        self.lb_phot.setPixmap(QPixmap().fromImage(img))

        for pos in select(pos for pos in SupplyPosition
                      if pos.parts.id == product.id and pos.supply.received and pos.warehouse_value):

            self.tw_product_warehouse.insertRow(self.tw_product_warehouse.rowCount())

            item = QTableWidgetItem(str(pos.supply.id))
            item.setData(5, pos.id)
            self.tw_product_warehouse.setItem(self.tw_product_warehouse.rowCount() - 1, 0, item)

            item = QTableWidgetItem(pos.supply.date_order.strftime("%d.%m.%Y"))
            item.setData(5, pos.id)
            self.tw_product_warehouse.setItem(self.tw_product_warehouse.rowCount() - 1, 1, item)

            item = QTableWidgetItem(pos.supply.date_shipping.strftime("%d.%m.%Y"))
            item.setData(5, pos.id)
            self.tw_product_warehouse.setItem(self.tw_product_warehouse.rowCount() - 1, 2, item)

            item = QTableWidgetItem(str(pos.value))
            item.setData(5, pos.id)
            self.tw_product_warehouse.setItem(self.tw_product_warehouse.rowCount() - 1, 3, item)

            item = QTableWidgetItem(str(pos.warehouse_value))
            item.setData(5, pos.id)
            self.tw_product_warehouse.setItem(self.tw_product_warehouse.rowCount() - 1, 4, item)

    @db_session
    def filter_machine(self):  # Выводит список оборудования в зависимости от фильтра
        query = """SELECT sewingmachine.id, sewingmachine.name, manufacturersewingmachine.name, GROUP_CONCAT(typesewingmachine.name)
                        FROM typesewingmachine
                          LEFT JOIN sewingmachine_typesewingmachine ON typesewingmachine.id = sewingmachine_typesewingmachine.typesewingmachine
                          LEFT JOIN sewingmachine ON sewingmachine_typesewingmachine.sewingmachine = sewingmachine.id
                          LEFT JOIN manufacturersewingmachine ON sewingmachine.manufacturer = manufacturersewingmachine.id"""

        where = ''
        if self.filter_machine_type_id:
            where += " typesewingmachine.id = %s" % self.filter_machine_type_id

        if self.filter_machine_man_id:
            if where:
                where += " AND "

            where += " manufacturersewingmachine.id = %s" % self.filter_machine_man_id

        if where:
            query += " WHERE " + where

        query += " GROUP BY sewingmachine"

        self.tw_machine.clearContents()
        self.tw_machine.setRowCount(0)

        list_table_item = db.select(query)
        for table_typle in list_table_item:
            self.tw_machine.insertRow(self.tw_machine.rowCount())
            for column in range(1, len(table_typle)):
                text = str(table_typle[column])
                item = QTableWidgetItem(text)
                item.setData(5, table_typle[0])
                self.tw_machine.setItem(self.tw_machine.rowCount() - 1, column - 1, item)

    @db_session
    def filter_product(self):  # Отфильтровываем товар
        query = select(p for p in Parts)

        if self.filter_article:  # Если мы ввели точны артикул то ищем только по нему
            query = query.filter(lambda p: self.filter_article == p.id)
            self.filter_article = None

        elif self.filter_name:
            query = query.filter(lambda p: self.filter_name in p.name)
            self.filter_name = None

        elif self.filter_manufacturer_name:
            query = query.filter(lambda p: self.filter_manufacturer_name in p.vendor_name)
            self.filter_manufacturer_name = None
        else:
            if self.filter_type_product_id:
                query = query.filter(lambda p: self.filter_type_product_id == p.tree.id)

            if self.filter_manufacturer_product_id:
                query = query.filter(lambda p: self.filter_manufacturer_product_id == p.manufacturer.id)

            if self.filter_machine_id:  # Если выбрана машина то фильтруем по ней
                query = query.filter(lambda p: self.filter_machine_id in p.sewing_machines.id)
            else:  # Если не выбрано обуродавания то можем фильровать по его параметрам
                if self.filter_machine_type_id:
                    query = query.filter(lambda p: self.filter_machine_type_id in p.sewing_machines.type.id)

                if self.filter_machine_man_id:
                    query = query.filter(lambda p: self.filter_machine_man_id in p.sewing_machines.manufacturer.id)

        result = query[:]

        self.set_products(result)

    def set_products(self, result):  # Вставить данные в таблицу товаров
        self.tw_poduct.clearContents()
        self.tw_poduct.setRowCount(0)

        if not result:
            return False

        self.tw_poduct.setSortingEnabled(False)

        table_result = [(p.id, p.id, p.name, p.manufacturer.name, p.price, p.note) for p in result]

        for row_result in table_result:
            self.tw_poduct.insertRow(self.tw_poduct.rowCount())
            for column in range(1, len(row_result)):
                item = QTableWidgetItem(str(row_result[column]))
                item.setData(5, row_result[0])
                self.tw_poduct.setItem(self.tw_poduct.rowCount() - 1, column - 1, item)

        self.tw_poduct.setSortingEnabled(True)

    def inspection_path(self, dir_name):  # Находим путь работника
        if not path.isdir("%s/%s" % (PHOTO_DIR, dir_name)):
            try:
                mkdir("%s/%s" % (PHOTO_DIR, dir_name))
                return "%s/%s" % (PHOTO_DIR, dir_name)
            except:
                QMessageBox.critical(self, "Ошибка файлы", "Нет доступа к корневому диалогу, файлы недоступны", QMessageBox.Ok)
                return False
        else:
            return "%s/%s" % (PHOTO_DIR, dir_name)

    def add_filter(self, where, add, and_add=True):
        if where:
            if and_add:
                where += " AND " + add
            else:
                where += " OR " + add
        else:
            where = add

        return where

    def search(self, id_tree, tree_class):  # Ищем ветви дерева и при этом добавляем их в QTreeWidgetItem
        item = QTreeWidgetItem((tree_class[id_tree].tag, ))  # Создаем полученый Id
        item.setData(0, 5, tree_class[id_tree].identifier)  # Добавляем ID
        for id in tree_class[id_tree].fpointer:  # Смотрим есть ли дети у этой ветви, если есть обзодим их
            item.addChild(self.search(id, tree_class))  # Добавляем детей этой ветви!

        return item

