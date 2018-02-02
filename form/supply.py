from os import getcwd, path, mkdir
from collections import namedtuple
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QDialog
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QImage, QPixmap, QBrush, QColor
from PyQt5.QtCore import Qt, QDate
from pony.orm import *
from my_class.orm_class import Parts, Supply, SupplyPosition, Vendor, CostOther, SupplyCostOther
from form import vendor, parts
from form.templates import table, list
from function.str_to import str_to_decimal


COLOR_WINDOW_SUPPLY = "204, 255, 0"
COLOR_WINDOW_COST_OTHER = "153, 153, 51"
PHOTO_DIR = getcwd() + "/photo/"


class SupplyList(table.TableList):
    def set_settings(self):
        self.setWindowTitle("Поставки товара")  # Имя окна
        self.resize(500, 270)
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_SUPPLY)  # Цвет бара

        self.pb_copy.deleteLater()
        self.pb_other.deleteLater()
        self.pb_filter.deleteLater()

        # Названия колонк (Имя, Длинна)
        self.table_header_name = (("№", 30), ("Поставщик", 75), ("Дата заказа", 80), ("Дата прихода", 80), ("Позиций", 55), ("Сумма", 75))

        self.item = Supply  # Класс который будем выводить! Без скобок!

        # сам запрос
        self.query = select((s.id, s.id, s.vendor.name, s.date_order, s.date_shipping, s.value_position, s.all_sum) for s in Supply)

    def ui_add_table_item(self):  # Добавить предмет
        self.add_supply = SupplyBrows(self)
        self.add_supply.setWindowModality(Qt.ApplicationModal)
        self.add_supply.show()

    def ui_change_table_item(self, item_id=False):  # изменить элемент
        if item_id:
            item_id = item_id
        else:
            try:
                item_id = self.table_widget.selectedItems()[0].data(5)
            except:
                QMessageBox.information(self, "Ошибка ", "Выделите элемент который хотите изменить", QMessageBox.Ok)
                return False

        self.supply = SupplyBrows(self, item_id)
        self.supply.setWindowModality(Qt.ApplicationModal)
        self.supply.show()

    def ui_double_click_table_item(self, item):  # Двойной клик по элементу
        if not self.dc_select:
            self.ui_change_table_item(item.data(5))
        else:
            # что хотим получить ставим всместо 0
            self.main.of_select_supply(item.data(5))
            self.close()
            self.destroy()


class SupplyBrows(QMainWindow):
    def __init__(self, main=None, supply_id=None):
        super(QMainWindow, self).__init__()
        loadUi(getcwd() + '/ui/supply.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_SUPPLY)

        self.main = main
        self.id = supply_id

        self.del_cost_id = set()  # тут хранятся Id для удаления растрат
        self.del_position_id = set()  # тут хранятся Id для удаления позиций

        self.start()

    @db_session
    def start(self):  # Стартовык настройки
        self.tw_cost_position.horizontalHeader().resizeSection(0, 100)
        self.tw_cost_position.horizontalHeader().resizeSection(1, 55)
        self.tw_cost_position.horizontalHeader().resizeSection(2, 55)
        self.tw_cost_position.horizontalHeader().resizeSection(3, 80)

        self.tw_position.horizontalHeader().resizeSection(0, 50)
        self.tw_position.horizontalHeader().resizeSection(1, 120)
        self.tw_position.horizontalHeader().resizeSection(2, 50)
        self.tw_position.horizontalHeader().resizeSection(3, 50)
        self.tw_position.horizontalHeader().resizeSection(4, 70)
        self.tw_position.horizontalHeader().resizeSection(5, 70)
        self.tw_position.horizontalHeader().resizeSection(6, 70)
        self.tw_position.horizontalHeader().resizeSection(7, 70)
        self.tw_position.horizontalHeader().resizeSection(8, 75)
        self.tw_position.horizontalHeader().resizeSection(9, 75)
        self.tw_position.horizontalHeader().resizeSection(10, 75)

        self.de_date_order.setDate(QDate.currentDate())
        self.de_date_shipping.setDate(QDate.currentDate())

        if self.id:  # Если есть ID то получим приход
            supply = Supply[self.id]

            self.le_id.setText(str(supply.id))
            self.de_date_order.setDate(supply.date_order)
            self.de_date_shipping.setDate(supply.date_shipping)
            self.cb_received.setChecked(supply.received)
            self.of_select_vendor(supply.vendor.id)
            self.le_city.setText(supply.city.name)
            self.le_city.setWhatsThis(str(supply.city.id))
            self.cb_shipping_method.setCurrentText(supply.shipping.name)
            self.cb_pay_method.setCurrentText(supply.payment.name)
            self.le_rate.setText(str(supply.rate))
            self.le_cost_sum.setText(str(supply.sum_cost))
            self.le_cost_percent.setText(str(supply.percent_cost))
            self.le_value_sum.setText(str(supply.value_position))
            self.le_sum_ru.setText(str(supply.position_sum))
            self.le_sum_all.setText(str(supply.all_sum))
            self.le_note.setText(supply.note)

            for cost in supply.cost_other:
                self.tw_cost_position.insertRow(self.tw_cost_position.rowCount())
                for i, cost_atr in enumerate((cost.cost_other.name, cost.price, cost.value, cost.sum)):
                    item = QTableWidgetItem(str(cost_atr))
                    if i == 0:  # Вставляем ID записи первую колонку!
                        item.setData(5, cost.id)
                    self.tw_cost_position.setItem(self.tw_cost_position.rowCount()-1, i, item)

            for position in supply.position:
                self.tw_position.insertRow(self.tw_position.rowCount())
                for i, position_atr in enumerate((position.parts.id, position.parts.name, position.value, position.warehouse_value, position.price_vendor, position.price_ru,
                                                  position.price_cost, position.percent_markup, position.price_sell, position.sum_ru, position.sum_cost)):
                    item = QTableWidgetItem(str(position_atr))
                    if i == 0:  # Вставляем ID записи первую колонку!
                        item.setData(5, position.id)
                    self.tw_position.setItem(self.tw_position.rowCount()-1, i, item)

    def ui_view_vendor(self):  # Открываем окно постаыщиков
        self.vendor = vendor.VendorList(self, dc_select=True)
        self.vendor.setWindowModality(Qt.ApplicationModal)
        self.vendor.show()

    def ui_add_cost(self):  # добавляем доп расход
        self.cost = SupplyCostOtherBrows()
        self.cost.setModal(True)
        self.cost.show()
        if self.cost.exec_() < 1:
            return False

        position = self.cost.acc_item
        col = 0
        self.tw_cost_position.insertRow(self.tw_cost_position.rowCount())

        for i in (position.cost, position.price, position.value, position.sum):
            item = QTableWidgetItem(str(i))
            if col == 0:  # Вставляем список со значениями только в первую колонку!
                item.setData(5, position)
            self.tw_cost_position.setItem(self.tw_cost_position.rowCount()-1, col, item)
            col += 1

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    def ui_change_cost(self, row):  # Менякм позицию расходов
        position = self.tw_cost_position.item(row, 0).data(5)

        self.cost = SupplyCostOtherBrows(position)
        self.cost.setModal(True)
        self.cost.show()
        if self.cost.exec_() < 1:
            return False

        position = self.cost.acc_item
        col = 0
        for i in (position.cost, position.price, position.value, position.sum):
            item = QTableWidgetItem(str(i))
            if col == 0:  # Вставляем список со значениями только в первую колонку!
                item.setData(5, position)
            self.tw_cost_position.setItem(row, col, item)
            col += 1

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    def ui_del_cost(self):  # Удаляем позицию расходов
        result = QMessageBox.question(self, "Удаление", "Точно удалить расход?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                row = self.tw_cost_position.currentRow()
            except:
                QMessageBox.critical(self, "Ошибка Удаления", "Выделите расход который хотите удалить", QMessageBox.Ok)
                return False

            position = self.tw_cost_position.item(row, 0).data(5)  # Смотрим какой тип лежит в дате (кортеж или просто ID)
            if isinstance(position, int):
                sql_id = position
            elif isinstance(position, str):
                sql_id = int(position)
            elif isinstance(position, tuple):
                sql_id = position.sql_id
            else:
                QMessageBox.critical(self, "Ошибка типа", "Пришел непонятный тип %s" % str(type(position)), QMessageBox.Ok)
                return False

            if sql_id is None:  # Если нет ID то можно спокойно удалить строку
                self.tw_cost_position.removeRow(row)
            else:
                self.del_cost_id.add(sql_id)
                self.tw_cost_position.removeRow(row)

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    def ui_add_position(self):  # Добавляем позию товара
        rate = str_to_decimal(self.le_rate.text())
        cost = str_to_decimal(self.le_cost_percent.text()) or 0
        if not rate:
            QMessageBox.information(self, "Ошибка", "Не выбрана затрата", QMessageBox.Ok)
            return False

        self.position = SupplyPositionBrows(rate, cost)
        self.position.setModal(True)
        self.position.show()
        if self.position.exec_() < 1:
            return False

        position = self.position.acc_item
        col = 0
        self.tw_position.insertRow(self.tw_position.rowCount())

        for i in (position.article, position.parts, position.value, position.warehouse_value, position.price_vendor, position.price_ru, position.price_cost,
                  position.percent_markup, position.price_sell, position.sum_ru, position.sum_cost):
            item = QTableWidgetItem(str(i))
            if col == 0:  # Вставляем список со значениями только в первую колонку!
                item.setData(5, position)
            self.tw_position.setItem(self.tw_position.rowCount()-1, col, item)
            col += 1

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    def ui_change_position(self):  # Меняем позицию товара
        try:
            row = self.tw_position.currentRow()
        except:
            QMessageBox.information(self, "Ошибка", "Выделите позицию которую хотите изменить", QMessageBox.Ok)
            return False
        if row == -1:
            QMessageBox.information(self, "Ошибка", "Выделите позицию которую хотите изменить", QMessageBox.Ok)
            return False

        position = self.tw_position.item(row, 0).data(5)
        rate = str_to_decimal(self.le_rate.text())
        cost = str_to_decimal(self.le_cost_percent.text()) or 0

        self.position = SupplyPositionBrows(rate, cost, position)
        self.position.setModal(True)
        self.position.show()
        if self.position.exec_() < 1:
            return False

        position = self.position.acc_item
        col = 0
        for i in (position.article, position.parts, position.value, position.warehouse_value, position.price_vendor, position.price_ru, position.price_cost,
                  position.percent_markup, position.price_sell, position.sum_ru, position.sum_cost):
            item = QTableWidgetItem(str(i))
            if col == 0:  # Вставляем список со значениями только в первую колонку!
                item.setData(5, position)
            self.tw_position.setItem(row, col, item)
            col += 1

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    def ui_del_position(self):  # Удаляем позицию товара
        result = QMessageBox.question(self, "Удаление", "Точно удалить товар?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if result == 16384:
            try:
                row = self.tw_position.currentRow()
            except:
                QMessageBox.critical(self, "Ошибка Удаления", "Выделите товар который хотите удалить", QMessageBox.Ok)
                return False

            position = self.tw_position.item(row, 0).data(5)  # Смотрим какой тип лежит в дате (кортеж или просто ID)
            if isinstance(position, int):
                sql_id = position
            elif isinstance(position, str):
                sql_id = int(position)
            elif isinstance(position, tuple):
                sql_id = position.sql_id
            else:
                QMessageBox.critical(self, "Ошибка типа", "Пришел непонятный тип %s" % str(type(position)), QMessageBox.Ok)
                return False

            if sql_id is None:  # Если нет ID то можно спокойно удалить строку
                self.tw_position.removeRow(row)
            else:
                self.del_position_id.add(sql_id)
                self.tw_position.removeRow(row)

        self.pb_acc.setEnabled(False)
        self.pb_calc.setStyleSheet("background-color: rgb(255, 61, 44);")

    @db_session
    def ui_calc_supply(self):  # Пересчет заказа (Затраты, сумма, позиции, ...)

        # узнать способ пересчета
        self.calc_way = SupplyCalcInquiry()
        self.calc_way.setModal(True)
        self.calc_way.show()
        if self.calc_way.exec_() < 1:
            return False

        self.PositionOrder = namedtuple('PositionOrder', """sql_id parts_id parts value warehouse_value price_vendor price_ru 
                                                            price_cost percent_markup price_sell price_profit sum_ru sum_cost article""")
        sum_cost = 0

        # Считаем сумму затрат
        for row in range(self.tw_cost_position.rowCount()):
            position = self.tw_cost_position.item(row, 0).data(5)

            if not isinstance(position, tuple):  # Тут получаем позицию из БД
                sql_position = SupplyCostOther[int(position)]  # Получаем позицию из бд
                pos_tuple = namedtuple('PositionCost', 'sql_id, cost_id cost value price sum')
                position = pos_tuple(sql_position.id, sql_position.cost_other.id, sql_position.cost_other.name,  # Составляем список для последующего сравнения
                                     sql_position.value, sql_position.price, sql_position.sum)

            sum_cost += position.sum

        # Считаем сумму заказа
        sum_ru = 0
        for row in range(self.tw_position.rowCount()):
            position = self.tw_position.item(row, 0).data(5)
            if not isinstance(position, tuple):
                sql_position = SupplyPosition[int(position)]  # Получаем позицию из бд
                position = self.PositionOrder(sql_position.id, sql_position.parts.id, sql_position.parts.name,  # Составляем список для последующего сравнения
                                              sql_position.value, sql_position.warehouse_value, sql_position.price_vendor, sql_position.price_ru,
                                              sql_position.price_cost, sql_position.percent_markup, sql_position.price_sell, sql_position.price_profit,
                                              sql_position.sum_ru, sql_position.sum_cost, sql_position.parts.id)
                self.tw_position.item(row, 0).setData(5, position)

            sum_ru += position.sum_ru

        # расчитываем затраты
        cost_percent = round(100 / (sum_ru / sum_cost), 2)
        sum_all_supply = sum_ru + sum_cost
        value_position = self.tw_position.rowCount()

        # Вставляем данные
        self.le_cost_sum.setText(str(round(sum_cost, 2)))
        self.le_cost_percent.setText(str(round(cost_percent, 2)))
        self.le_value_sum.setText(str(round(value_position, 2)))
        self.le_sum_ru.setText(str(round(sum_ru, 2)))
        self.le_sum_all.setText(str(round(sum_all_supply, 2)))

        # пересчитываем позиции
        for row in range(self.tw_position.rowCount()):
            position = self.tw_position.item(row, 0).data(5)

            new_price_cost = round(((position.price_ru / 100) * cost_percent) + position.price_ru, 2)  # новая себестоимость

            if self.calc_way == 2:  # Если пересчитываем процент наценки
                position = self.PositionOrder(position.sql_id,
                                              position.parts_id,
                                              position.parts,
                                              position.value,
                                              position.warehouse_value,
                                              position.price_vendor,
                                              position.price_ru,
                                              new_price_cost,
                                              round((position.price_sell - new_price_cost) / new_price_cost * 100, 2),
                                              position.price_sell,
                                              round(position.price_sell - new_price_cost, 2),
                                              position.sum_ru,
                                              round(new_price_cost * position.value, 2))

            elif self.calc_way == 1:  # Если пересчитываем цену

                new_price_sell = round(((new_price_cost / 100) * position.percent_markup) + new_price_cost, 2)

                position = self.PositionOrder(position.sql_id,
                                              position.parts_id,
                                              position.parts,
                                              position.value,
                                              position.warehouse_value,
                                              position.price_vendor,
                                              position.price_ru,
                                              new_price_cost,
                                              position.percent_markup,
                                              new_price_sell,
                                              round(new_price_sell - new_price_cost, 2),
                                              position.sum_ru,
                                              round(new_price_cost * position.value, 2))

            # Вставляем пересчитаный кортеж в строку
            self.tw_position.item(row, 0).setData(5, position)
            # Проверяем остались ли мы в прибыли. (помечем цветом)
            if position.price_profit > 0:
                color = QBrush(QColor(150, 255, 161, 255))
            else:
                color = QBrush(QColor(252, 141, 141, 255))

            # обновляем саму строку
            col = 0
            for i in (position.article, position.parts, position.value, position.warehouse_value, position.price_vendor, position.price_ru, position.price_cost,
                      position.percent_markup, position.price_sell, position.sum_ru, position.sum_cost):
                item = QTableWidgetItem(str(i))
                item.setBackground(color)
                if col == 0:  # Вставляем список со значениями только в первую колонку!
                    item.setData(5, position)
                self.tw_position.setItem(row, col, item)
                col += 1

        self.pb_acc.setEnabled(True)
        self.pb_calc.setStyleSheet("background-color: rgb(85, 255, 0);")

    @db_session
    def ui_acc(self):
        value = {
                "date_order": self.de_date_order.date().toPyDate(),
                "date_shipping": self.de_date_shipping.date().toPyDate(),
                "received": self.cb_received.isChecked(),
                "rate": str_to_decimal(self.le_rate.text()),
                "percent_cost": str_to_decimal(self.le_cost_percent.text()),
                "sum_cost": str_to_decimal(self.le_cost_sum.text()),
                "position_sum": str_to_decimal(self.le_sum_ru.text()),
                "all_sum": str_to_decimal(self.le_sum_all.text()),
                "value_position": int(self.le_value_sum.text()),
                "note": self.le_note.text(),
                "vendor": int(self.le_vendor.whatsThis()),
                "city": int(self.le_city.whatsThis()),
                "shipping": self.cb_shipping_method.currentData(),
                "payment": self.cb_pay_method.currentData()
                }

        if self.id:
            supply = Supply[self.id]
            supply.set(**value)
        else:
            supply = Supply(**value)

        for row in range(self.tw_cost_position.rowCount()):  # Добавим или обновим затраты
            position = self.tw_cost_position.item(row, 0).data(5)
            if not isinstance(position, tuple):  # Если не список то ненадо сохранять ничего
                continue

            value = {
                    "cost_other": position.cost_id,
                    "value": position.value,
                    "price": position.price,
                    "sum": position.sum,
                    "supply": supply}

            if position.sql_id is None:
                supply.cost_other.add(SupplyCostOther(**value))
            else:
                CostOther[position.sql_id].set(**value)

        for row in range(self.tw_position.rowCount()):  # Добавим или обновим позиции
            position = self.tw_position.item(row, 0).data(5)
            if not isinstance(position, tuple):  # Если не список то ненадо сохранять ничего
                continue
            value = {
                    "value": position.value,
                    "warehouse_value": position.warehouse_value,
                    "price_vendor": position.price_vendor,
                    "price_ru": position.price_ru,
                    "price_cost": position.price_cost,
                    "percent_markup": position.percent_markup,
                    "price_sell": position.price_sell,
                    "price_profit": position.price_profit,
                    "sum_ru": position.sum_ru,
                    "sum_cost": position.sum_cost,
                    "supply": supply,
                    "parts": position.parts_id}

            if position.sql_id is None:
                supply.position.add(SupplyPosition(**value))
            else:
                SupplyPosition[position.sql_id].set(**value)

        # Удалим позиции
        for id in self.del_cost_id:
            CostOther[id].delete()
        for id in self.del_position_id:
            SupplyPosition[id].delete()

        self.main.ui_update()
        self.close()
        self.destroy()

    def ui_can(self):
        self.close()
        self.destroy()

    @db_session
    def of_select_vendor(self, vendor_id):  # Вставляем поставщика + его города и способы доставки и оплаты
        vendor = Vendor[vendor_id]
        self.le_vendor.setText(vendor.name)
        self.le_vendor.setWhatsThis(str(vendor.id))

        self.le_city.setText(vendor.city.name)
        self.le_city.setWhatsThis(str(vendor.city.id))

        for ship in vendor.shipping_methods:
            self.cb_shipping_method.addItem(ship.name, ship.id)

        for pay in vendor.payment_methods:
            self.cb_pay_method.addItem(pay.name, pay.id)


class SupplyPositionBrows(QDialog):
    def __init__(self, rate=0, cost=0, position=None):
        super(SupplyPositionBrows, self).__init__()
        loadUi(getcwd() + '/ui/supply_position.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_SUPPLY)

        self.rate = rate
        self.cost = cost
        self.position = position

        self.part = None  # переменная хранящая ORM класс запчасти
        self.sql_id = None  # ID sql позиции
        self.sql_sel = None  # Записываем сколько было продано товара для расчета склада
        self.acc_item = None  # переменная для хранения итогово списка

        self.PositionOrder = namedtuple('PositionOrder', """sql_id parts_id parts value warehouse_value price_vendor price_ru 
                                                            price_cost percent_markup price_sell price_profit sum_ru sum_cost article""")   # Переменная хранения позиции

        self.start()

    @db_session
    def start(self):  # выставить стартовые настройки
        self.le_cost.setText(str(self.cost))

        # Проверим что пришло, список или Id строки
        if isinstance(self.position, tuple):
            self.sql_id = self.position.sql_id
            self.sql_sel = self.position.value - self.position.warehouse_value

            self.le_article.setWhatsThis(str(self.position.parts_id))
            self.le_article.setText(str(self.position.article))
            self.le_part.setWhatsThis(str(self.position.parts_id))
            self.le_part.setText(str(self.position.parts))
            self.le_value.setText(str(self.position.value))
            self.le_warehouse.setText(str(self.position.warehouse_value))
            self.le_price_ven.setText(str(self.position.price_vendor))
            self.le_price_ru.setText(str(self.position.price_ru))
            self.le_price_a_cost.setText(str(self.position.price_cost))
            self.le_markup.setText(str(self.position.percent_markup))
            self.le_price_sel.setText(str(self.position.price_sell))
            self.le_price_profit.setText(str(self.position.price_profit))
            self.le_sum_ru.setText(str(self.position.sum_ru))
            self.le_sum_a_cost.setText(str(self.position.sum_cost))

            self.ui_calc_sum()
            self.ui_calc_markup_percent()
            self.calc_profit()
            self.calc_cost_percent()

        elif isinstance(self.position, int):
            self.sql_id = self.position  # Записываем Id строки
            sql_position = SupplyPosition[self.sql_id]  # Получаем позицию из бд
            self.sql_sel = sql_position.value - sql_position.warehouse_value

            self.position = self.PositionOrder(self.sql_id, sql_position.parts.id, sql_position.parts.name,  # Составляем список для последующего сравнения
                                               sql_position.value, sql_position.warehouse_value, sql_position.price_vendor, sql_position.price_ru,
                                               sql_position.price_cost, sql_position.percent_markup, sql_position.price_sell, sql_position.price_profit,
                                               sql_position.sum_ru, sql_position.sum_cost, sql_position.parts.id)

            self.le_article.setWhatsThis(str(self.position.parts_id))
            self.le_article.setText(str(self.position.article))
            self.le_part.setWhatsThis(str(self.position.parts_id))
            self.le_part.setText(str(self.position.parts))
            self.le_value.setText(str(self.position.value))
            self.le_warehouse.setText(str(self.position.warehouse_value))
            self.le_price_ven.setText(str(self.position.price_vendor))
            self.le_price_ru.setText(str(self.position.price_ru))
            self.le_price_a_cost.setText(str(self.position.price_cost))
            self.le_markup.setText(str(self.position.percent_markup))
            self.le_price_sel.setText(str(self.position.price_sell))
            self.le_price_profit.setText(str(self.position.price_profit))
            self.le_sum_ru.setText(str(self.position.sum_ru))
            self.le_sum_a_cost.setText(str(self.position.sum_cost))

            self.tb_product.setEnabled(False)

            self.ui_calc_sum()
            self.ui_calc_markup_percent()
            self.calc_profit()
            self.calc_cost_percent()

        elif self.position is None:  # Новая позиция
            self.sql_sel = 0
            self.sql_id = None

        else:
            QMessageBox.information(self, "Ошибка типа", "Пришел непонятный тип %s" % str(type(self.position)), QMessageBox.Ok)
            return False

    def ui_view_parts(self):  # Показать окно выбора запчасти
        self.parts = parts.PartsList(self, True)
        self.parts.setWindowModality(Qt.ApplicationModal)
        self.parts.show()

    def ui_acc(self):
        if not self.le_part.text():
            QMessageBox.information(self, "Ошибка", "Не выбран товар", QMessageBox.Ok)
            return False

        self.acc_item = self.PositionOrder(self.sql_id,
                                           int(self.le_part.whatsThis()),
                                           self.le_part.text(),
                                           str_to_decimal(self.le_value.text()),
                                           str_to_decimal(self.le_warehouse.text()),
                                           str_to_decimal(self.le_price_ven.text()),
                                           str_to_decimal(self.le_price_ru.text()),
                                           str_to_decimal(self.le_price_a_cost.text()),
                                           str_to_decimal(self.le_markup.text()),
                                           str_to_decimal(self.le_price_sel.text()),
                                           str_to_decimal(self.le_price_profit.text()),
                                           str_to_decimal(self.le_sum_ru.text()),
                                           str_to_decimal(self.le_sum_a_cost.text()),
                                           self.le_article.text())

        if self.position == self.acc_item:  # Если позиция не изменилась то дклаем закрытие окна
            print("нет изменений в пизиции")
            self.ui_can()
            return False

        # Проверим список на заполненость! Кроме первого значения. Там может быть None если это новая позиция
        for item in tuple(self.acc_item)[1:]:
            if not item:
                QMessageBox.information(self, "Ошибка заполнения", "Что то не заполнено", QMessageBox.Ok)
                return False

        self.done(1)
        self.close()
        self.destroy()

    def ui_can(self):
        self.done(0)
        self.close()
        self.destroy()

    def ui_get_parts_price(self):  # Получение цены продажи из карточки товара
        if self.part:
            self.le_price_sel.setText(str(self.part.price))
            self.ui_calc_sum()
            self.ui_calc_markup_percent()

    def ui_calc_warehouse(self):  # Пересчитывем склад
        new_value = str_to_decimal(self.le_value.text())
        if new_value:
                if (new_value - self.sql_sel) < 0:  # Если новое кол-во неподходит
                    self.le_value.setText("Не меньше %s" % self.sql_sel)
                    return False

                else:
                    self.le_warehouse.setText(str(new_value - self.sql_sel))
                    return True

    def ui_calc_price_vendor(self):  # посчитать цену продавца от курса
        price_ru = str_to_decimal(self.le_price_ru.text())
        sum_ru = str_to_decimal(self.le_sum_ru.text())

        if price_ru:
            self.le_price_ven.setText(str(round(price_ru / self.rate, 2)))

        if sum_ru:
            self.le_sum_ven.setText(str(round(sum_ru / self.rate, 2)))

    def ui_calc_price_ru(self):  # посчитать цену в рублях от курса
        price_vendor = str_to_decimal(self.le_price_ven.text())
        sum_vendor = str_to_decimal(self.le_sum_ven.text())

        if price_vendor:
            self.le_price_ru.setText(str(round(price_vendor * self.rate, 2)))

        if sum_vendor:
            self.le_sum_ru.setText(str(round(sum_vendor * self.rate, 2)))

        self.ui_calc_price_a_cost()

    def ui_calc_sum(self):  # Считаем сумму цены продавца и рублей и с наценкой
        value = str_to_decimal(self.le_value.text())
        price_vendor = str_to_decimal(self.le_price_ven.text())
        price_ru = str_to_decimal(self.le_price_ru.text())
        price_sel = str_to_decimal(self.le_price_sel.text())

        if value and price_vendor:
            self.le_sum_ven.setText(str(round(value * price_vendor, 2)))

        if value and price_ru:
            self.le_sum_ru.setText(str(round(value * price_ru, 2)))

        if value and price_sel:
            self.le_sum_sel.setText(str(round(value * price_sel, 2)))

    def ui_calc_pcs(self):  # Считаем цены продавца и рублей и с наценкой
        value = str_to_decimal(self.le_value.text())
        sum_vendor = str_to_decimal(self.le_sum_ven.text())
        sum_ru = str_to_decimal(self.le_sum_ru.text())
        sum_sel = str_to_decimal(self.le_sum_sel.text())

        if value and sum_vendor:
            self.le_price_ven.setText(str(round(sum_vendor / value, 2)))

        if value and sum_ru:
            self.le_price_ru.setText(str(round(sum_ru / value, 2)))

        if value and sum_sel:
            self.le_price_sel.setText(str(round(sum_sel / value, 2)))

        self.ui_calc_markup_percent()

    def ui_calc_price_a_cost(self):  # Считаем цену + расходы
        price_ru = str_to_decimal(self.le_price_ru.text())
        sum_ru = str_to_decimal(self.le_sum_ru.text())
        cost = str_to_decimal(self.le_cost.text())

        if price_ru:
            self.le_price_a_cost.setText(str(round(((price_ru / 100) * cost) + price_ru, 4)))

        if sum_ru:
            self.le_sum_a_cost.setText(str(round(((sum_ru / 100) * cost) + sum_ru, 4)))

        self.ui_calc_markup_percent()

    def ui_calc_markup_percent(self):  # считаем % наценки
        price_a_rate = str_to_decimal(self.le_price_a_cost.text())
        price_sel = str_to_decimal(self.le_price_sel.text())

        if price_a_rate and price_sel:
            self.le_markup.setText(str(round((price_sel - price_a_rate) / price_a_rate * 100, 2)))

        self.calc_profit()

    def ui_calc_markup(self):  # считаем цену от % наценки
        price_a_rate = str_to_decimal(self.le_price_a_cost.text())
        sum_a_cost = str_to_decimal(self.le_sum_a_cost.text())
        markup_percent = str_to_decimal(self.le_markup.text())

        if price_a_rate and markup_percent:
            self.le_price_sel.setText(str(round(((price_a_rate / 100) * markup_percent) + price_a_rate, 2)))

        if sum_a_cost and markup_percent:
            self.le_sum_sel.setText(str(round(((sum_a_cost / 100) * markup_percent) + sum_a_cost, 2)))

        self.calc_profit()

    def calc_profit(self):  # Считаем прибыль
        price_a_rate = str_to_decimal(self.le_price_a_cost.text())
        sum_a_rate = str_to_decimal(self.le_sum_a_cost.text())
        price_markup = str_to_decimal(self.le_price_sel.text())
        sum_markup = str_to_decimal(self.le_sum_sel.text())

        if price_a_rate and price_markup:
            self.le_price_profit.setText(str(round(price_markup - price_a_rate, 2)))
        if sum_a_rate and sum_markup:
            self.le_sum_profit.setText(str(round(sum_markup - sum_a_rate, 2)))

    def calc_cost_percent(self):  # Считаем проент расходов
        price_ru = str_to_decimal(self.le_price_ru.text())
        price_a_cost = str_to_decimal(self.le_price_a_cost.text())

        if price_ru and price_a_cost:
            self.le_cost.setText(str(round(100 / (price_ru / price_a_cost) - 100, 2)))

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

    @db_session
    def of_tree_select_product(self, part_id):
        self.part = Parts[part_id]
        self.le_part.setText(self.part.name)
        self.le_part.setWhatsThis(str(self.part.id))

        self.le_article.setText(str(self.part.id))
        self.le_article.setWhatsThis(str(self.part.id))

        path_photo = self.inspection_path(self.part.id)
        img = QImage(path_photo + "/main.jpg")
        img = img.scaled(self.lb_photo.height(), self.lb_photo.width(), Qt.KeepAspectRatio)
        self.lb_photo.setPixmap(QPixmap().fromImage(img))


class SupplyCostOtherList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Список прочих затрат")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_COST_OTHER)  # Цвет бара

        self.item = CostOther

        self.set_new_win = {"WinTitle": "Затрата",
                            "WinColor": "(%s)" % COLOR_WINDOW_COST_OTHER,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_other_cost(select_prov.data(5))
            self.close()
            self.destroy()


class SupplyCostOtherBrows(QDialog):
    def __init__(self, position=None):
        super(SupplyCostOtherBrows, self).__init__()
        loadUi(getcwd() + '/ui/supply_cost.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.widget.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_COST_OTHER)

        self.PositionCost = namedtuple('PositionCost', 'sql_id, cost_id cost value price sum')

        self.position = position

        self.sql_id = None  # переменная для хранения и вставки sql ID строки
        self.acc_item = None  # переменная для хранения итогово списка

        self.start()

    @db_session
    def start(self):
        # Проверим что пришло, список или Id строки
        if isinstance(self.position, tuple):
            self.sql_id = self.position.sql_id
            self.le_cost.setWhatsThis(str(self.position.cost_id))
            self.le_cost.setText(str(self.position.cost))
            self.le_value.setText(str(self.position.value))
            self.le_price.setText(str(self.position.price))
            self.le_sum.setText(str(self.position.sum))

        elif isinstance(self.position, int):
            self.sql_id = self.position  # Записываем Id строки
            sql_position = SupplyCostOther[self.sql_id]  # Получаем позицию из бд
            self.position = self.PositionCost(self.sql_id, sql_position.cost_other.id, sql_position.cost_other.name,  # Составляем список для последующего сравнения
                                              sql_position.value, sql_position.price, sql_position.sum)
            self.le_cost.setWhatsThis(str(self.position.cost_id))
            self.le_cost.setText(str(self.position.cost))
            self.le_value.setText(str(self.position.value))
            self.le_price.setText(str(self.position.price))
            self.le_sum.setText(str(self.position.sum))

        elif self.position is None:  # Новая позиция
            pass

        else:
            QMessageBox.information(self, "Ошибка типа", "Пришел непонятный тип %s" % str(type(self.position)), QMessageBox.Ok)
            return False

    def ui_view_cost_other(self):
        self.cost_other = SupplyCostOtherList(self, True)
        self.cost_other.setWindowModality(Qt.ApplicationModal)
        self.cost_other.show()

    def ui_acc(self):
        if not self.le_cost.text():
            QMessageBox.information(self, "Ошибка", "Не выбрана затрата", QMessageBox.Ok)
            return False

        self.acc_item = self.PositionCost(self.sql_id,
                                          int(self.le_cost.whatsThis()),
                                          self.le_cost.text(),
                                          int(self.le_value.text()),
                                          str_to_decimal(self.le_price.text()),
                                          str_to_decimal(self.le_sum.text()))

        if self.acc_item == self.position:  # Если позиция не изменилась то дклаем закрытие окна
            print("нет изменений в прочих расходах")
            self.ui_can()
            return False

        if not self.acc_item.value:
            QMessageBox.information(self, "Ошибка", "Что то не так с кол-вом", QMessageBox.Ok)
            return False

        if not self.acc_item.price:
            QMessageBox.information(self, "Ошибка", "Что то не так с ценой", QMessageBox.Ok)
            return False

        if not self.acc_item.sum:
            QMessageBox.information(self, "Ошибка", "Что то не так с суммой", QMessageBox.Ok)
            return False

        self.done(1)
        self.close()
        self.destroy()

    def ui_can(self):
        self.done(0)
        self.close()
        self.destroy()

    def ui_calc_sum(self):
        value = str_to_decimal(self.le_value.text())
        price = str_to_decimal(self.le_price.text())

        if value and price:
            self.le_sum.setText(str(round(value*price, 2)))
        else:
            self.le_sum.setText("ОШИБКА")

    def ui_calc_pcs(self):
        value = str_to_decimal(self.le_value.text())
        sum = str_to_decimal(self.le_sum.text())

        if value and sum:
            self.le_sum.setText(str(round(sum/value, 2)))
        else:
            self.le_sum.setText("ОШИБКА")

    @db_session
    def of_list_select_other_cost(self, cost_id):
        cost = CostOther[cost_id]
        self.le_cost.setText(cost.name)
        self.le_cost.setWhatsThis(str(cost.id))


class SupplyCalcInquiry(QDialog):  # окно справшивающее что пересчитывать в приходе
    def __init__(self):
        super(SupplyCalcInquiry, self).__init__()
        loadUi(getcwd() + '/ui/supply_calc.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

    def ui_percent(self):  # Оставить процент наценки
        self.done(1)
        self.close()
        self.destroy()

    def ui_price(self):  # Оставить цену товара
        self.done(2)
        self.close()
        self.destroy()
