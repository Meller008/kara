from form.templates import list
from my_class.orm import Country


class CountryList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Страны")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(0, 170, 255);")  # Цвет бара

        self.item = Country

        self.set_new_win = {"WinTitle": "Страна",
                            "WinColor": "(0, 170, 255)",
                            "lb_name": "Название",
                            "lb_note": "Заметка"}
