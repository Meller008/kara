from pony.orm import *


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


class PaymentMethodVendor(db.Entity):
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
    city = Required('CityVendor')
    shipping_methods = Set(ShippingMethodVendor)
    payment_methods = Set(PaymentMethodVendor)


class CityVendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    country = Required(CountryVendor)
    vendors = Set(Vendor)


class Parts(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str)
    note = Optional(str)
    manufacturer = Required('ManufacturerParts')
    sewing_machines = Set('SewingMachine')
    tree = Required('PartsTree')


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

sql_debug(True)
db.generate_mapping(create_tables=True, check_tables=True)
