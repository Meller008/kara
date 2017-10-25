from form.templates import list
from my_class.orm_class import PaymentMethod


COLOR_WINDOW = "255, 51, 0"


class PaymentMethodList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Способы оплаты")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.item = PaymentMethod

        self.set_new_win = {"WinTitle": "Способ оплаты",
                            "WinColor": "(%s)" % COLOR_WINDOW,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_payment_method(select_prov.data(5))
            self.close()
            self.destroy()
