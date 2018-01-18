from pony.orm import *
from datetime import date
from decimal import Decimal
from collections import namedtuple


db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class CountryVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    city = Set('CityVendor')


class ShippingMethodVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')
    supplys = Set('Supply')


class PaymentMethodVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')
    supplys = Set('Supply')


class Vendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    full_name = Optional(str)
    mail = Optional(str)
    note = Optional(str)
    phone = Optional(str)
    site = Optional(str)
    city = Required('CityVendor')
    shipping_methods = Set(ShippingMethodVendor)
    payment_methods = Set(PaymentMethodVendor)
    supplys = Set('Supply')


class Parts(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    manufacturer = Required('ManufacturerParts')
    price = Required(Decimal)
    tree = Required('PartsTree')
    supply_positions = Set('SupplyPosition')
    sewing_machines = Set('SewingMachine')


class PartsTree(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    parent = Required(int)
    position = Optional(int, default=20)
    parts = Set(Parts)


class ManufacturerParts(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    parts = Set(Parts)


class CostOther(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    supply_cost_others = Set('SupplyCostOther')


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
    cost_other = Set('SupplyCostOther')
    city = Required('CityVendor')
    shipping = Required(ShippingMethodVendor)
    payment = Required(PaymentMethodVendor)
    vendor = Required(Vendor)
    position = Set('SupplyPosition')


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


class SupplyCostOther(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Optional(int)
    price = Optional(Decimal)
    sum = Required(Decimal)
    supply = Required(Supply)
    cost_other = Required(CostOther)


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
    sewing_machines = Set(SewingMachine)


class TypeSewingMachine(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    note = Optional(str)
    sewing_machines = Set(SewingMachine)


class CityVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    country = Required(CountryVendor)
    supplys = Set(Supply)
    vendors = Set(Vendor)

sql_debug(True)
db.generate_mapping(create_tables=True, check_tables=True)
