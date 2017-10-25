from pony.orm import *


db = Database()


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