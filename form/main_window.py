from os import getcwd
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
from form import country, shipping, payment

main_class = loadUiType(getcwd() + '/ui/main_window.ui')[0]


class MainWindow(QMainWindow, main_class):
    def __init__(self, *args):
        super(MainWindow, self).__init__(*args)
        self.setupUi(self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

        self.show()

    def ui_view_country(self):
        self.country = country.CountryList()
        self.sub_country = QMdiSubWindow()
        self.sub_country.setWidget(self.country)
        self.mdi.addSubWindow(self.sub_country)
        self.sub_country.resize(self.country.size())
        self.sub_country.show()

    def ui_view_shipping_method(self):
        self.shipping_method = shipping.ShippingMethodList()
        self.sub_shipping_method = QMdiSubWindow()
        self.sub_shipping_method.setWidget(self.shipping_method)
        self.mdi.addSubWindow(self.sub_shipping_method)
        self.sub_shipping_method.resize(self.shipping_method.size())
        self.sub_shipping_method.show()

    def ui_view_payment_method(self):
        self.Payment_method = payment.PaymentMethodList()
        self.sub_Payment_method = QMdiSubWindow()
        self.sub_Payment_method.setWidget(self.Payment_method)
        self.mdi.addSubWindow(self.sub_Payment_method)
        self.sub_Payment_method.resize(self.Payment_method.size())
        self.sub_Payment_method.show()