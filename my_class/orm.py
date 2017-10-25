from pony.orm import *


db = Database()
db.bind(provider='mysql', host='192.168.1.24', user='kara', passwd='Aa088011', db='kara')


class Country(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    vendors = Set('Vendor')
    note = Optional(str)


class ShippingMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    vendors = Set('Vendor')
    note = Optional(str)


class PaymentMethod(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    vendors = Set('Vendor')
    note = Optional(str)


class Vendor(db.Entity):
    id = PrimaryKey(int, auto=True)
    country = Required(Country)
    shipping_method = Required(ShippingMethod)
    payment_method = Required(PaymentMethod)
    name = Required(str)
    full_name = Optional(str)
    mail = Optional(str)
    note = Optional(str)
    phone = Optional(str)
    site = Optional(str)


sql_debug(True)
db.generate_mapping(create_tables=True, check_tables=True)
