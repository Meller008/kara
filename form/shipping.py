from form.templates import list
from my_class.orm_class import ShippingMethod


COLOR_WINDOW = "204, 102, 0"


class ShippingMethodList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Способы доставки")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.item = ShippingMethod

        self.set_new_win = {"WinTitle": "Способ доставки",
                            "WinColor": "(%s)" % COLOR_WINDOW,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_shipping_method(select_prov.data(5))
            self.close()
            self.destroy()
