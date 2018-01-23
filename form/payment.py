from form.templates import list
from my_class.orm_class import PaymentMethodVendor, PaymentMethod


COLOR_WINDOW_VENDOR = "255, 51, 0"
COLOR_WINDOW_CLIENT = "178, 34, 34"


class PaymentMethodVendorList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Способы оплаты поставщику")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_VENDOR)  # Цвет бара

        self.item = PaymentMethodVendor

        self.set_new_win = {"WinTitle": "Способ оплаты",
                            "WinColor": "(%s)" % COLOR_WINDOW_VENDOR,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_payment_method(select_prov.data(5))
            self.close()
            self.destroy()


class PaymentMethodClientList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Способы оплаты клиента")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_CLIENT)  # Цвет бара

        self.item = PaymentMethod

        self.set_new_win = {"WinTitle": "Способ оплаты",
                            "WinColor": "(%s)" % COLOR_WINDOW_CLIENT,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_payment_method_client(select_prov.data(5))
            self.close()
            self.destroy()

