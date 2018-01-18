from os import getcwd, path, mkdir, remove
import shutil
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtCore import Qt
from my_class.orm_class import Parts, PartsTree, ManufacturerParts, SewingMachine
from form.templates import tree, list
from form import sewing_machine
from function.str_to import str_to_float
from pony.orm import *

COLOR_WINDOW_PARTS = "0, 102, 102"
COLOR_WINDOW_PARTS_MANUFACTURER = "204, 255, 255"
PHOTO_DIR = getcwd() + "/photo/"


class PartsList(tree.TreeList):
    def set_settings(self):
        self.setWindowTitle("Список товара")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS)  # Цвет бара

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("Артикул", 100), ("Имя", 150), ("Цена", 200))

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

    def ui_add_table_item(self):  # Добавить предмет
        try:
            tree_id = self.tree_widget.selectedItems()[0].data(0, 5)
        except:
            QMessageBox.critical(self, "Ошибка ", "Выделите элемент дерева куда добавлять предмет", QMessageBox.Ok)
            return False
        if tree_id < 0:
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


class PartsWindow(QMainWindow):
    def __init__(self, main=None, product_id=None, tree_id=None):
        super(PartsWindow, self).__init__()
        loadUi(getcwd() + '/ui/product.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_PARTS)

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

    @db_session
    def ui_acc(self):

        value = {
                "name": self.le_name.text(),
                "note": self.le_note.text(),
                "manufacturer": self.le_manufacturer.whatsThis(),
                "tree": self.tree_id,
                "price": str_to_float(self.le_price.text())
                }

        if self.id:
            p = Parts[self.id]
            value.pop("tree")
            p.set(**value)
        else:
            p = Parts(**value)

        p.sewing_machines.remove(map(lambda x: SewingMachine[x], self.machine_id_del))
        p.sewing_machines.add(map(lambda x: SewingMachine[x], self.machine_id_new))

        commit()

        if self.photo_del or self.photo_dir:
            path_photo = self.inspection_path(p.id)
            if path_photo:
                if self.photo_del:
                    path_photo += "/main.jpg"
                    remove(path_photo)

                if self.photo_dir:
                    path_photo += "/main.jpg"
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