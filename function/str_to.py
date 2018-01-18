from decimal import Decimal

def str_to_float(str_in):
    if not str_in:
        return None

    try:
        fl = float(str_in.replace(',', "."))
        return fl
    except ValueError:
        return False

def str_to_decimal(str_in):
    if not str_in:
        return None

    try:
        fl = Decimal(str_in.replace(',', "."))
        return fl
    except:
        return False
