from pony.orm import *


db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class Country(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')


class ShippingMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')


class PaymentMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    note = Optional(str)
    vendors = Set('Vendor')


class Vendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    full_name = Optional(str)
    mail = Optional(str)
    note = Optional(str)
    phone = Optional(str)
    site = Optional(str)
    country = Required(Country)
    shipping_methods = Set(ShippingMethod)
    payment_methods = Set(PaymentMethod)


class SewingMachine(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    note = Optional(str)
    manufacturer = Required('ManufacturerSewingMachine')
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


sql_debug(True)
db.generate_mapping(create_tables=True, check_tables=True)
