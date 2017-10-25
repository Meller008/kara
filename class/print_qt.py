import os
import codecs
from PyQt5 import QtWebKitWidgets
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import QPrintPreviewDialog, QPrinter


class PrintHtml(QtWebKitWidgets.QWebView):
    def __init__(self, parent=None, html=None):
        super(PrintHtml, self).__init__(parent)

        # html = codecs.open(b"template.html", encoding='utf-8').read()
        baseurl = QUrl.fromLocalFile(os.getcwd() + "/temp/index.html")
        self.setHtml(html, baseurl)
        self.printer = QPrinter()
        self.printer.setPageSize(QPrinter.A4)
        self.printer.setOrientation(QPrinter.Portrait)
        self.printer.setPageMargins(5, 5, 5, 5, QPrinter.Millimeter)
        self.setFixedWidth(1000)

        dialog = QPrintPreviewDialog(self.printer)
        dialog.setWindowState(Qt.WindowMaximized)
        dialog.paintRequested.connect(self.print_)
        dialog.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint | Qt.WindowContextHelpButtonHint)
        dialog.exec()