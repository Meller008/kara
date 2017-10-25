from form.templates import list
from my_class.orm import PaymentMethod


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
