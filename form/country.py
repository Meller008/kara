from form.templates import list
from my_class.orm_class import Country

COLOR_WINDOW = "255, 255, 51"


class CountryList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Страны")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW)  # Цвет бара

        self.item = Country

        self.set_new_win = {"WinTitle": "Страна",
                            "WinColor": "(%s)" % COLOR_WINDOW,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}
