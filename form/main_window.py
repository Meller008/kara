from os import getcwd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QBrush, QImage
from form import country, shipping, payment, vendor, sewing_machine, parts, supply, clients, order, label,\
    calc_delivery, site


class MainWindow(QMainWindow):
    def __init__(self, win_arg):
        super(MainWindow, self).__init__()
        loadUi(getcwd() + '/ui/main_window.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))
        self.mdi.setBackground(QBrush(QImage(getcwd() + "/images/logo_mdi.png")))

        self.tabWidget.setTabIcon(0, QIcon(getcwd() + "/images/supply.ico"))
        self.tabWidget.setTabIcon(1, QIcon(getcwd() + "/images/order.ico"))
        self.tabWidget.setTabIcon(2, QIcon(getcwd() + "/images/product.ico"))
        self.tabWidget.setTabIcon(3, QIcon(getcwd() + "/images/machine.ico"))
        self.tabWidget.setTabIcon(4, QIcon(getcwd() + "/images/warehouse.ico"))
        self.tabWidget.setTabIcon(5, QIcon(getcwd() + "/images/other_tab.ico"))

        if "-C" in win_arg:
            self.arg_C()

        if "-FS" in win_arg:
            self.arg_FS()

        self.show()

    def ui_view_supply(self):
        self.supply = supply.SupplyList()
        self.sub_supply = QMdiSubWindow()
        self.sub_supply.setWidget(self.supply)
        self.mdi.addSubWindow(self.sub_supply)
        self.sub_supply.resize(self.supply.size())
        self.sub_supply.show()

    def ui_view_supply_other_cost(self):
        self.supply_other_cost = supply.SupplyCostOtherList()
        self.sub_supply_other_cost = QMdiSubWindow()
        self.sub_supply_other_cost.setWidget(self.supply_other_cost)
        self.mdi.addSubWindow(self.sub_supply_other_cost)
        self.sub_supply_other_cost.resize(self.supply_other_cost.size())
        self.sub_supply_other_cost.show()

    def ui_view_country(self):
        self.country = country.CountryVendorList()
        self.sub_country = QMdiSubWindow()
        self.sub_country.setWidget(self.country)
        self.mdi.addSubWindow(self.sub_country)
        self.sub_country.resize(self.country.size())
        self.sub_country.show()

    def ui_view_city(self):
        self.city_vendor = country.CityVendorList()
        self.sub_city_vendor = QMdiSubWindow()
        self.sub_city_vendor.setWidget(self.city_vendor)
        self.mdi.addSubWindow(self.sub_city_vendor)
        self.sub_city_vendor.resize(self.city_vendor.size())
        self.sub_city_vendor.show()

    def ui_view_shipping_method(self):
        self.shipping_method = shipping.ShippingMethodVendorList()
        self.sub_shipping_method = QMdiSubWindow()
        self.sub_shipping_method.setWidget(self.shipping_method)
        self.mdi.addSubWindow(self.sub_shipping_method)
        self.sub_shipping_method.resize(self.shipping_method.size())
        self.sub_shipping_method.show()

    def ui_view_payment_method(self):
        self.Payment_method = payment.PaymentMethodVendorList()
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
        self.sewing_machine = sewing_machine.SewingMachineList()
        self.sub_sewing_machine = QMdiSubWindow()
        self.sub_sewing_machine.setWidget(self.sewing_machine)
        self.mdi.addSubWindow(self.sub_sewing_machine)
        self.sub_sewing_machine.resize(self.sewing_machine.size())
        self.sub_sewing_machine.show()

    def ui_view_parts_list(self):
        self.parts_list = parts.PartsList()
        self.sub_parts_list = QMdiSubWindow()
        self.sub_parts_list.setWidget(self.parts_list)
        self.mdi.addSubWindow(self.sub_parts_list)
        self.sub_parts_list.resize(self.parts_list.size())
        self.sub_parts_list.show()

    def ui_view_parts_catalog(self):
        self.parts_catalog = parts.PartsCatalog()
        self.sub_parts_catalog = QMdiSubWindow()
        self.sub_parts_catalog.setWidget(self.parts_catalog)
        self.mdi.addSubWindow(self.sub_parts_catalog)
        self.sub_parts_catalog.resize(self.parts_catalog.size())
        self.sub_parts_catalog.show()

    def ui_view_parts_manufacturer_list(self):
        self.parts_manufacturer_list = parts.PartsManufacturer()
        self.sub_parts_manufacturer_list = QMdiSubWindow()
        self.sub_parts_manufacturer_list.setWidget(self.parts_manufacturer_list)
        self.mdi.addSubWindow(self.sub_parts_manufacturer_list)
        self.sub_parts_manufacturer_list.resize(self.parts_manufacturer_list.size())
        self.sub_parts_manufacturer_list.show()

    def ui_view_shipping_client_list(self):
        self.shipping_client_list = shipping.ShippingMethodClientList()
        self.sub_shipping_client_list = QMdiSubWindow()
        self.sub_shipping_client_list.setWidget(self.shipping_client_list)
        self.mdi.addSubWindow(self.sub_shipping_client_list)
        self.sub_shipping_client_list.resize(self.shipping_client_list.size())
        self.sub_shipping_client_list.show()

    def ui_view_payment_client_list(self):
        self.payment_client_list = payment.PaymentMethodClientList()
        self.sub_payment_client_list = QMdiSubWindow()
        self.sub_payment_client_list.setWidget(self.payment_client_list)
        self.mdi.addSubWindow(self.sub_payment_client_list)
        self.sub_payment_client_list.resize(self.payment_client_list.size())
        self.sub_payment_client_list.show()

    def ui_view_city_client_list(self):
        self.city_client_list = country.CityClientList()
        self.sub_city_client_list = QMdiSubWindow()
        self.sub_city_client_list.setWidget(self.city_client_list)
        self.mdi.addSubWindow(self.sub_city_client_list)
        self.sub_city_client_list.resize(self.city_client_list.size())
        self.sub_city_client_list.show()

    def ui_view_client_list(self):
        self.client_list = clients.ClientList()
        self.sub_client_list = QMdiSubWindow()
        self.sub_client_list.setWidget(self.client_list)
        self.mdi.addSubWindow(self.sub_client_list)
        self.sub_client_list.resize(self.client_list.size())
        self.sub_client_list.show()

    def ui_view_order_list(self):
        self.order_list = order.OrderList()
        self.sub_order_list = QMdiSubWindow()
        self.sub_order_list.setWidget(self.order_list)
        self.mdi.addSubWindow(self.sub_order_list)
        self.sub_order_list.resize(self.order_list.size())
        self.sub_order_list.show()

    def ui_view_label_box(self):
        self.label_box = label.LabelBox()
        self.sub_label_box = QMdiSubWindow()
        self.sub_label_box.setWidget(self.label_box)
        self.mdi.addSubWindow(self.sub_label_box)
        self.sub_label_box.resize(self.label_box.size())
        self.sub_label_box.show()

    def ui_view_calc_delivery(self):
        self.calc_delivery = calc_delivery.CalcDelivery()
        self.sub_calc_delivery = QMdiSubWindow()
        self.sub_calc_delivery.setWidget(self.calc_delivery)
        self.mdi.addSubWindow(self.sub_calc_delivery)
        self.sub_calc_delivery.resize(self.calc_delivery.size())
        self.sub_calc_delivery.show()

    def ui_view_export_site_product(self):
        self.site_export = site.SiteExportProduct()
        self.sub_site_export = QMdiSubWindow()
        self.sub_site_export.setWidget(self.site_export)
        self.mdi.addSubWindow(self.sub_site_export)
        self.sub_site_export.resize(self.site_export.size())
        self.sub_site_export.show()

    def ui_view_photo_site(self):
        self.photo_site = site.ExportPhotoSite()
        # self.sub_photo_site = QMdiSubWindow()
        # self.sub_photo_site.setWidget(self.photo_site)
        # self.mdi.addSubWindow(self.sub_photo_site)
        # self.sub_photo_site.resize(self.photo_site.size())
        # self.sub_photo_site.show()

    def arg_C(self):
        self.tabWidget.setEnabled(False)
        self.ui_view_parts_catalog()

    def arg_FS(self):
        self.setWindowState(Qt.WindowMaximized)
