from os import getcwd, path as pathh
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QFileDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDateTime
from pony.orm import *
from my_class.orm_class import Parts, SupplyPosition
from form import parts
from function.translate import translate
from function.str_to import str_to_decimal
import openpyxl

IGNORE_CATEGORIES = 59
SITE_ADD_TEXT = ", купить в магазине КАРА"


class SiteExportProduct(QMainWindow):
    def __init__(self):
        super(SiteExportProduct, self).__init__()
        loadUi(getcwd() + '/ui/site_export.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.tw_position.horizontalHeader().resizeSection(0, 60)
        self.tw_position.horizontalHeader().resizeSection(1, 170)
        self.tw_position.horizontalHeader().resizeSection(2, 150)
        self.tw_position.horizontalHeader().resizeSection(3, 150)
        self.tw_position.horizontalHeader().resizeSection(4, 150)

    def ui_file_brows(self):
        path = QFileDialog.getOpenFileName(self, "Сохранение", pathh.expanduser("~/Desktop/"), filter="Excel(*.xlsx)")
        if not path[0]:
            return False

        self.le_path.setText(path[0])

    def ui_add_position(self):
        self.parts = parts.PartsCatalog(self, select_product=True)
        self.parts.setWindowModality(Qt.ApplicationModal)
        self.parts.show()

    def ui_dell_position(self):
        try:
            row = self.tw_position.currentRow()
        except:
            return False

        if row >= 0:
            self.tw_position.removeRow(row)

    def ui_open_product(self, row):
        _id = int(self.tw_position.item(row, 0).text())

        self.parts = parts.PartsWindow(product_id=_id)
        self.parts.setWindowModality(Qt.ApplicationModal)
        self.parts.show()

    @db_session
    def ui_add_all_position(self):
        for parts in Parts.select(lambda p: p.tree.id != IGNORE_CATEGORIES):
            row = self.tw_position.rowCount()
            self.tw_position.insertRow(self.tw_position.rowCount())

            item = QTableWidgetItem(str(parts.id))
            self.tw_position.setItem(row, 0, item)

            item = QTableWidgetItem(str(parts.name))
            self.tw_position.setItem(row, 1, item)

            item = QTableWidgetItem(str(parts.site_info.seo_keyword))
            self.tw_position.setItem(row, 2, item)

            item = QTableWidgetItem(str(parts.site_info.title))
            self.tw_position.setItem(row, 3, item)

            item = QTableWidgetItem(str(parts.site_info.h1))
            self.tw_position.setItem(row, 4, item)

    @db_session
    def ui_export(self):
        if not self.le_path.text():
            QMessageBox.information(self, "Фаил", "Выберите фаил для экспорта", QMessageBox.Ok)
            return False

        self.statusBar.showMessage("Проверка позиций")
        if not self.ui_checking_position():
            return False

        book = openpyxl.load_workbook(filename=self.le_path.text())
        sheet = book['Products']

        row_excel = 2
        max_id = 0
        excel_article = {}  # {Артикул: строка}

        # Составим список уже записанных артикулов!
        self.statusBar.showMessage("Проверка записанных артикулов")
        while True:
            if not sheet["E%s" % row_excel].value:
                break

            excel_article.update({int(sheet["E%s" % row_excel].value): row_excel})

            if int(sheet["A%s" % row_excel].value) > max_id:
                max_id = int(sheet["A%s" % row_excel].value)
            row_excel += 1

        # Начнем записывать артикула
        date_now = QDateTime.currentDateTime()
        for row in range(self.tw_position.rowCount()):
            _id = int(self.tw_position.item(row, 0).text())
            _parts = Parts[_id]
            self.statusBar.showMessage("Вставка артикула %s" % str(_id))

            # Узнаем в какую строку будем записывать!
            if excel_article.get(_parts.id):  # Если такой артикул уже есть
                select_row_excel = excel_article.get(_parts.id)
                id_select = sheet["A%s" % select_row_excel].value
            else:
                max_id += 1
                select_row_excel = row_excel
                id_select = max_id
                row_excel += 1

            # Запишем товар в фаил
            sheet["A%s" % select_row_excel] = id_select
            sheet["B%s" % select_row_excel] = _parts.site_info.name
            sheet["C%s" % select_row_excel] = _parts.site_info.main_category
            sheet["D%s" % select_row_excel] = _parts.site_info.categories
            sheet["E%s" % select_row_excel] = str(_parts.id).zfill(5)
            sheet["L%s" % select_row_excel] = 10
            sheet["M%s" % select_row_excel] = str(_parts.id).zfill(5)
            sheet["O%s" % select_row_excel] = "catalog/product/%s.jpg" % _parts.id
            sheet["P%s" % select_row_excel] = "yes"
            sheet["Q%s" % select_row_excel] = str(_parts.site_info.price)
            sheet["R%s" % select_row_excel] = 0
            sheet["S%s" % select_row_excel] = date_now.toString("yyyy-dd-MM HH:mm:ss")
            sheet["T%s" % select_row_excel] = date_now.toString("yyyy-dd-MM HH:mm:ss")
            sheet["U%s" % select_row_excel] = date_now.toString("yyyy-dd-MM")
            sheet["V%s" % select_row_excel] = 0
            sheet["W%s" % select_row_excel] = "кг"
            sheet["X%s" % select_row_excel] = 0
            sheet["Y%s" % select_row_excel] = 0
            sheet["Z%s" % select_row_excel] = 0
            sheet["AA%s" % select_row_excel] = "см"
            sheet["AB%s" % select_row_excel] = "true"
            sheet["AC%s" % select_row_excel] = 0
            sheet["AD%s" % select_row_excel] = _parts.site_info.seo_keyword
            sheet["AE%s" % select_row_excel] = _parts.site_info.description
            sheet["AF%s" % select_row_excel] = _parts.site_info.title
            sheet["AG%s" % select_row_excel] = _parts.site_info.meta_description
            sheet["AH%s" % select_row_excel] = _parts.site_info.h1
            sheet["AI%s" % select_row_excel] = ""
            sheet["AJ%s" % select_row_excel] = 7
            sheet["AK%s" % select_row_excel] = 0
            sheet["AO%s" % select_row_excel] = 1
            sheet["AP%s" % select_row_excel] = "false"
            sheet["AQ%s" % select_row_excel] = 1

        self.statusBar.showMessage("Сохранение нового файла")
        book.save(self.le_path.text().replace(".xlsx", "_new.xlsx"))
        self.statusBar.showMessage("Готово!")

    @db_session
    def ui_generation(self):
        for row in range(self.tw_position.rowCount()):
            _id = int(self.tw_position.item(row, 0).text())
            _parts = Parts[_id]
            self.statusBar.showMessage("Генерация артикула %s" % str(_id))

            if not self.rb_all.isChecked:
                if _parts.site_info.id:
                    if _parts.site_info.name or _parts.site_info.in_warehouse or _parts.site_info.seo_keyword \
                            or _parts.site_info.title or _parts.site_info.meta_description or _parts.site_info.h1 \
                            or _parts.site_info.categories or _parts.site_info.main_category:
                        continue

            _parts.site_info.name = _parts.name
            _parts.site_info.title = _parts.name + SITE_ADD_TEXT
            _parts.site_info.h1 = _parts.name
            _parts.site_info.seo_keyword = translate(_parts.name)
            _parts.site_info.meta_description = _parts.name + SITE_ADD_TEXT

            for_text = ""
            if _parts.note:
                for_text += "<p>%s</p>" % _parts.note

            if _parts.sewing_machines:
                for_text += "<p><b>Подходит</b></p><ul>"
                for sw in _parts.sewing_machines:
                    for_text += "<li>%s %s</li>" % (sw.manufacturer.name, sw.name)
                else:
                    for_text += "</ul>"

            _parts.site_info.description = for_text

            supplies = select(supply for supply in SupplyPosition if supply.parts == _parts and supply.warehouse_value > 0).order_by(
                lambda s: s.supply.date_shipping)[:1]
            if supplies:
                _parts.site_info.in_warehouse = True
                _parts.site_info.price = supplies[0].price_sell
            else:
                _parts.site_info.in_warehouse = False
                _parts.site_info.price = 0

    @db_session
    def ui_checking_position(self):
        if self.cb_view_none.isChecked():
            for row in range(self.tw_position.rowCount()):
                _id = int(self.tw_position.item(row, 0).text())
                p = Parts[_id]

                if self.cb_view_none.isChecked():
                    if p.site_info.id:
                        if not p.site_info.name or not p.site_info.in_warehouse or not p.site_info.seo_keyword \
                                or not p.site_info.title or not p.site_info.meta_description or not p.site_info.h1 \
                                or not p.site_info.categories or not p.site_info.main_category:
                            self.tw_position.setCurrentCell(row, 0)
                            QMessageBox.information(self, "Пусто", "Арикул %s не заполнен для сайта" % _id, QMessageBox.Ok)
                            return False
                    else:
                        self.tw_position.setCurrentCell(row, 0)
                        QMessageBox.information(self, "Пусто", "Арикул %s не заполнен для сайта" % _id, QMessageBox.Ok)
                        return False

        return True

    @db_session
    def of_tree_select_catalog_product(self, _id):
        parts = Parts[_id]

        row = self.tw_position.rowCount()
        self.tw_position.insertRow(self.tw_position.rowCount())

        item = QTableWidgetItem(str(parts.id))
        self.tw_position.setItem(row, 0, item)

        item = QTableWidgetItem(str(parts.name))
        self.tw_position.setItem(row, 1, item)

        item = QTableWidgetItem(str(parts.site_info.seo_keyword))
        self.tw_position.setItem(row, 2, item)

        item = QTableWidgetItem(str(parts.site_info.title))
        self.tw_position.setItem(row, 3, item)

        item = QTableWidgetItem(str(parts.site_info.h1))
        self.tw_position.setItem(row, 4, item)
