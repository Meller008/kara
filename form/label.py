from os import getcwd
from collections import namedtuple
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from pony.orm import *
from my_class.orm_class import Parts
from form import parts
from my_class import print_qt


class LabelBox(QMainWindow):
    def __init__(self):
        super(LabelBox, self).__init__()
        loadUi(getcwd() + '/ui/print_label_box.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.Label = namedtuple('PositionOrder', """width height font row1 row2 row3""")
        self.select_row = None

        self.start()

    def start(self):
        self.tw_label.horizontalHeader().resizeSection(0, 50)
        self.tw_label.horizontalHeader().resizeSection(1, 50)
        self.tw_label.horizontalHeader().resizeSection(2, 50)
        self.tw_label.horizontalHeader().resizeSection(3, 200)
        self.tw_label.horizontalHeader().resizeSection(4, 200)
        self.tw_label.horizontalHeader().resizeSection(5, 200)

        for i in ("84", "122", "207"):
            self.cb_width.addItem(i)

        for i in ("48", ):
            self.cb_height.addItem(i)

        for i in range(19, 21):
            self.cb_font_size.addItem(str(i))

    def ui_view_product(self):
        self.parts = parts.PartsList(self, True)
        self.parts.setWindowModality(Qt.ApplicationModal)
        self.parts.show()

    def ui_add_label(self):
        self.tw_label.insertRow(self.tw_label.rowCount())
        item = QTableWidgetItem("new")
        item.setData(5, None)
        self.tw_label.setItem(self.tw_label.rowCount()-1, 0, item)

    def ui_select_label(self, row):
        if self.select_row is not None:
            new_label = self.Label(self.cb_width.currentText(), self.cb_height.currentText(), self.cb_font_size.currentText(),
                                   self.le_row1.toPlainText(), self.le_row2.toPlainText(), self.le_row3.toPlainText())

            item = QTableWidgetItem(self.cb_width.currentText())
            item.setData(5, new_label)
            self.tw_label.setItem(self.select_row, 0, item)

            item = QTableWidgetItem(self.cb_height.currentText())
            self.tw_label.setItem(self.select_row, 1, item)

            item = QTableWidgetItem(self.cb_font_size.currentText())
            self.tw_label.setItem(self.select_row, 2, item)

            item = QTableWidgetItem(self.le_row1.toPlainText())
            self.tw_label.setItem(self.select_row, 3, item)

            item = QTableWidgetItem(self.le_row2.toPlainText())
            self.tw_label.setItem(self.select_row, 4, item)

            item = QTableWidgetItem(self.le_row3.toPlainText())
            self.tw_label.setItem(self.select_row, 5, item)

        self.cb_width.setEditText("")
        self.cb_height.setEditText("")
        self.cb_font_size.setEditText("")
        self.le_row1.setPlainText("")
        self.le_row2.setPlainText("")
        self.le_row3.setPlainText("")

        self.select_row = row
        label = self.tw_label.item(row, 0).data(5)

        if label:
            self.cb_width.setEditText(label.width)
            self.cb_height.setEditText(label.height)
            self.cb_font_size.setEditText(label.font)

            self.le_row1.setPlainText(label.row1)
            self.le_row2.setPlainText(label.row2)
            self.le_row3.setPlainText(label.row3)

    def ui_del_label(self):
        try:
            row = self.tw_label.currentRow()
            self.tw_label.removeRow(row)
        except:
            return False

        self.select_row = None

        self.cb_width.setEditText("")
        self.cb_height.setEditText("")
        self.cb_font_size.setEditText("")
        self.le_row1.setPlainText("")
        self.le_row2.setPlainText("")
        self.le_row3.setPlainText("")

    def ui_very_small_label(self):
        self.cb_width.setEditText("67")
        self.cb_height.setEditText("15")
        self.cb_font_size.setEditText("12")

    def ui_small_label(self):
        self.cb_width.setCurrentIndex(0)
        self.cb_height.setCurrentIndex(0)
        self.cb_font_size.setCurrentIndex(1)

    def ui_medium_label(self):
        self.cb_width.setCurrentIndex(1)
        self.cb_height.setCurrentIndex(0)
        self.cb_font_size.setCurrentIndex(1)

    def ui_large_label(self):
        self.cb_width.setCurrentIndex(2)
        self.cb_height.setCurrentIndex(0)
        self.cb_font_size.setCurrentIndex(1)

    def ui_acc(self):
        if self.select_row is not None:
            new_label = self.Label(self.cb_width.currentText(), self.cb_height.currentText(), self.cb_font_size.currentText(),
                                   self.le_row1.toPlainText(), self.le_row2.toPlainText(), self.le_row3.toPlainText())

            item = QTableWidgetItem(self.cb_width.currentText())
            item.setData(5, new_label)
            self.tw_label.setItem(self.select_row, 0, item)

        html_table = """<table border="1" style=" width: #WIDTHmm; height: #HEIGHTmm; border-collapse: collapse; text-align: center; font-size: #FONTpx;">
                        <tr><th>#ROW1</th></tr>
                        <tr><td>#ROW2</td></tr>
                        <tr><td>#ROW3</td></tr>
                        </table>"""

        html_all = ""

        for row in range(self.tw_label.rowCount()):
            label = self.tw_label.item(row, 0).data(5)
            if not label:
                continue

            new_table = html_table
            new_table = new_table.replace("#WIDTH", label.width)
            new_table = new_table.replace("#HEIGHT", label.height)
            new_table = new_table.replace("#FONT", label.font)
            new_table = new_table.replace("#ROW1", label.row1.replace("\n", "<br>"))
            new_table = new_table.replace("#ROW2", label.row2.replace("\n", "<br>"))
            new_table = new_table.replace("#ROW3", label.row3.replace("\n", "<br>"))

            html_all += " " + new_table

        print_qt.PrintHtml(self, html_all)

    def ui_can(self):
        self.close()
        self.destroy()

    @db_session
    def of_tree_select_product(self, part_id):
        part = Parts[part_id]

        row1 = self.le_row1.toPlainText()
        row2 = self.le_row2.toPlainText()
        row3 = self.le_row3.toPlainText()

        if row1:
            row1 += " "
        row1 += str(part.id).zfill(3)
        if row2:
            row2 += " "
        row2 += part.name
        if row3:
            row3 += " "
        row3 += part.note

        self.le_row1.setPlainText(row1)
        self.le_row2.setPlainText(row2)
        self.le_row3.setPlainText(row3)

