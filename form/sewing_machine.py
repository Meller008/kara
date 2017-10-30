from form.templates import list
from my_class.orm_class import ManufacturerSewingMachine, TypeSewingMachine, SewingMachine


COLOR_WINDOW_MANUFACTURER = "102, 0, 255"
COLOR_WINDOW_TYPE = "51, 51, 255"
COLOR_WINDOW_MACHINE = "102, 153, 255"


class TypeMachineList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Типы машин")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_TYPE)  # Цвет бара

        self.item = TypeSewingMachine

        self.set_new_win = {"WinTitle": "Тип машины",
                            "WinColor": "(%s)" % COLOR_WINDOW_TYPE,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_manufacturer_machine(select_prov.data(5))
            self.close()
            self.destroy()


class ManufacturerMachineList(list.ListItems):
    def set_settings(self):
        self.setWindowTitle("Производители машин")  # Имя окна
        self.toolBar.setStyleSheet("background-color: rgb(%s);" % COLOR_WINDOW_MANUFACTURER)  # Цвет бара

        self.item = ManufacturerSewingMachine

        self.set_new_win = {"WinTitle": "Производитель",
                            "WinColor": "(%s)" % COLOR_WINDOW_MANUFACTURER,
                            "lb_name": "Название",
                            "lb_note": "Заметка"}

    def ui_double_click_item(self, select_prov):
        if not self.dc_select:
            self.ui_change_item(select_prov.data(5))
        else:
            self.m_class.of_list_select_manufacturer_machine(select_prov.data(5))
            self.close()
            self.destroy()
