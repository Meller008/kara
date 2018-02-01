from datetime import date
from decimal import Decimal
from pony.orm import *


db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class CountryVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    city = Set('CityVendor', cascade_delete=False)


class ShippingMethodVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')
    supplys = Set('Supply', cascade_delete=False)


class PaymentMethodVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')
    supplys = Set('Supply', cascade_delete=False)


class Vendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    full_name = Optional(str)
    phone = Optional(str)
    mail = Optional(str)
    site = Optional(str)
    note = Optional(str)
    city = Required('CityVendor')
    shipping_methods = Set(ShippingMethodVendor)
    payment_methods = Set(PaymentMethodVendor)
    supplys = Set('Supply', cascade_delete=False)


class Order(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(date)
    sum_shipping = Optional(Decimal)
    sum_position = Required(Decimal)
    sum_discount = Required(Decimal)
    sum_all = Required(Decimal)
    value_position = Required(int)
    discount_percent = Required(Decimal)
    note = Optional(str)
    client = Required('Client')
    shipping_method = Required('ShippingMethod')
    payment_method = Required('PaymentMethod')
    order_positions = Set('OrderPosition', cascade_delete=False)


class CityClient(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    clients = Set('Client', cascade_delete=False)


class OrderPosition(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Required(Decimal)
    price = Required(Decimal)
    sum = Required(Decimal)
    supply_position = Required('SupplyPosition')
    order = Required(Order)


class Parts(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str, unique=True)
    vendor_name = Optional(str, unique=True)
    note = Optional(str)
    manufacturer = Required('ManufacturerParts')
    price = Required(Decimal)
    tree = Required('PartsTree')
    supply_positions = Set('SupplyPosition', cascade_delete=False)
    sewing_machines = Set('SewingMachine')


class SewingMachine(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    note = Optional(str)
    manufacturer = Required('ManufacturerSewingMachine')
    parts = Set(Parts)
    type = Set('TypeSewingMachine')


class ManufacturerSewingMachine(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    note = Optional(str)
    sewing_machines = Set(SewingMachine, cascade_delete=False)


class PartsTree(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    parent = Required(int)
    position = Optional(int, default=20)
    parts = Set(Parts, cascade_delete=False)


class CostOther(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    supply_cost_others = Set('SupplyCostOther', cascade_delete=False)


class TypeSewingMachine(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    note = Optional(str)
    sewing_machines = Set(SewingMachine)


class ManufacturerParts(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    parts = Set(Parts, cascade_delete=False)


class Supply(db.Entity):
    id = PrimaryKey(int, auto=True)
    date_order = Required(date)
    date_shipping = Optional(date)
    received = Required(bool)
    rate = Required(Decimal)
    percent_cost = Optional(Decimal)
    sum_cost = Required(Decimal)
    position_sum = Optional(Decimal)
    all_sum = Optional(Decimal)
    value_position = Required(int)
    note = Optional(str)
    cost_other = Set('SupplyCostOther', cascade_delete=False)
    city = Required('CityVendor')
    shipping = Required(ShippingMethodVendor)
    payment = Required(PaymentMethodVendor)
    vendor = Required(Vendor)
    position = Set('SupplyPosition', cascade_delete=False)


class SupplyPosition(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Required(Decimal)
    warehouse_value = Required(Decimal)
    price_vendor = Required(Decimal)
    price_ru = Required(Decimal)
    price_cost = Optional(Decimal)
    percent_markup = Optional(Decimal)
    price_sell = Optional(Decimal)
    price_profit = Optional(Decimal)
    sum_ru = Required(Decimal)
    sum_cost = Required(Decimal)
    supply = Required(Supply)
    parts = Required(Parts)
    order_positions = Set(OrderPosition, cascade_delete=False)


class Client(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    full_name = Optional(str)
    fio = Optional(str)
    phone = Optional(str)
    mail = Optional(str)
    site = Optional(str)
    addres_legal = Optional(str)
    addres_actual = Optional(str)
    inn = Optional(int)
    kpp = Optional(int)
    ogrn = Optional(int)
    bik = Optional(int)
    account = Optional(int)
    bank = Optional(str)
    corres_account = Optional(int)
    note = Optional(str)
    city = Required(CityClient)
    orders = Set(Order, cascade_delete=False)


class CityVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    country = Required(CountryVendor)
    supplys = Set(Supply, cascade_delete=False)
    vendors = Set(Vendor, cascade_delete=False)


class SupplyCostOther(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Optional(int)
    price = Optional(Decimal)
    sum = Required(Decimal)
    supply = Required(Supply)
    cost_other = Required(CostOther)


class ShippingMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    orders = Set(Order, cascade_delete=False)


class PaymentMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    orders = Set(Order, cascade_delete=False)

sql_debug(True)
db.generate_mapping(create_tables=True, check_tables=True)