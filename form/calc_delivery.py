from os import getcwd
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon


class CalcDelivery(QMainWindow):
    def __init__(self):
        super(CalcDelivery, self).__init__()
        loadUi(getcwd() + '/ui/calc_delivery.ui', self)
        self.setWindowIcon(QIcon(getcwd() + "/images/icon.ico"))

    def ui_calc(self):

        # Получаем общие данные
        try:
            invoice = float(self.le_invoice.text().replace(",", "."))
            rate = float(self.le_rate_dol.text().replace(",", "."))
            kg = float(self.le_kg.text().replace(",", "."))
        except:
            return False

        # Считаем отправку денег
        try:
            per_sent = float(self.le_per_sent.text().replace(",", "."))
            per_convert = float(self.le_per_convert.text().replace(",", "."))

            all_per = per_sent + per_convert
            sum_sent_d = round((invoice / 100) * all_per, 2)

            self.le_per_sum_sent.setText(str(round(all_per, 2)))
            self.le_sum_d.setText(str(round(sum_sent_d, 2)))
            self.le_sum_r.setText(str(round(sum_sent_d * rate, 2)))
            self.le_all_sent_d.setText(str(round(sum_sent_d + invoice, 2)))
            self.le_all_sent_r.setText(str(round((sum_sent_d + invoice) * rate, 2)))
        except:
            return False

        # Считаем доставку
        try:
            price_kg = float(self.le_price_kg_d.text().replace(",", "."))
            per_insurance = float(self.le_per_insurance.text().replace(",", "."))

            sum_kg_d = price_kg * kg
            sum_insurance_d = round((invoice / 100) * per_insurance, 2)
            all_sum_delivery = sum_kg_d + sum_insurance_d
            per_delivery = 100 / (invoice / sum_kg_d)

            all_per_delivery = per_delivery + per_insurance

            self.le_price_kg_r.setText(str(round(price_kg * rate, 2)))
            self.le_per_delivery.setText(str(round(per_delivery, 2)))
            self.le_sum_delivery_d.setText(str(round(sum_kg_d, 2)))
            self.le_sum_delivery_r.setText(str(round(sum_kg_d * rate, 2)))
            self.le_sum_insurance_d.setText(str(round(sum_insurance_d, 2)))
            self.le_sum_insurance_r.setText(str(round(sum_insurance_d * rate, 2)))
            self.le_all_sum_d.setText(str(round(all_sum_delivery, 2)))
            self.le_all_sum_r.setText(str(round(all_sum_delivery * rate, 2)))
            self.le_all_delivery_d.setText(str(round(invoice + all_sum_delivery, 2)))
            self.le_all_delivery_r.setText(str(round((invoice + all_sum_delivery) * rate, 2)))
        except:
            return False

        # Считаем доп затраты
        try:
            cost_d = float(self.le_cost_d.text())

            if cost_d:
                cost_per = round(100 / (invoice / cost_d), 2)
            else:
                cost_per = 0

            self.le_cost_per.setText(str(round(cost_per, 2)))

        except:
            return False

        self.le_all_per_perevod.setText(str(round(all_per, 2)))
        self.le_all_per_delivery.setText(str(round(all_per_delivery, 2)))
        self.le_all_per_cost.setText(str(round(cost_per, 2)))
        self.le_all_per.setText(str(round(cost_per + all_per_delivery + all_per, 2)))

        self.le_all_sum_perevod_d.setText(str(round(sum_sent_d, 2)))
        self.le_all_sum_perevod_r.setText(str(round(sum_sent_d * rate, 2)))
        self.le_all_sum_delivery_d.setText(str(round(all_sum_delivery, 2)))
        self.le_all_sum_delivery_r.setText(str(round(all_sum_delivery * rate, 2)))
        self.le_all_sum_cost_d.setText(str(round(cost_d, 2)))
        self.le_all_sum_cost_r.setText(str(round(cost_d * rate, 2)))

        all_sum = sum_sent_d + all_sum_delivery + cost_d

        self.le_all_sum_d_2.setText(str(round(all_sum, 2)))
        self.le_all_sum_r_2.setText(str(round(all_sum * rate, 2)))
        self.le_invoice_d.setText(str(round(invoice, 2)))
        self.le_invoice_r.setText(str(round(invoice * rate, 2)))
        self.le_all_order_sum_d.setText(str(round(all_sum + invoice, 2)))
        self.le_all_order_sum_r.setText(str(round((all_sum + invoice) * rate, 2)))
