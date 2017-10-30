from os import getcwd
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
from form import country, shipping, payment, vendor, sewing_machine

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

    def ui_view_vendor(self):
        self.vendor = vendor.VendorList()
        self.sub_vendor = QMdiSubWindow()
        self.sub_vendor.setWidget(self.vendor)
        self.mdi.addSubWindow(self.sub_vendor)
        self.sub_vendor.resize(self.vendor.size())
        self.sub_vendor.show()

    def ui_view_manufacturer_machine(self):
        self.manufacturer_machine = sewing_machine.ManufacturerMachineList()
        self.sub_manufacturer_machine = QMdiSubWindow()
        self.sub_manufacturer_machine.setWidget(self.manufacturer_machine)
        self.mdi.addSubWindow(self.sub_manufacturer_machine)
        self.sub_manufacturer_machine.resize(self.manufacturer_machine.size())
        self.sub_manufacturer_machine.show()

    def ui_view_type_machine(self):
        self.type_machine = sewing_machine.TypeMachineList()
        self.sub_type_machine = QMdiSubWindow()
        self.sub_type_machine.setWidget(self.type_machine)
        self.mdi.addSubWindow(self.sub_type_machine)
        self.sub_type_machine.resize(self.type_machine.size())
        self.sub_type_machine.show()

    def ui_view_sewing_machine(self):
        pass