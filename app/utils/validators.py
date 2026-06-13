import re


def validate_sku(sku):
    return bool(re.match(r'^[A-Za-z0-9\-_]+$', sku))


def validate_phone(phone):
    return bool(re.match(r'^\+?1?\d{10,15}$', phone))


def validate_pincode(pincode):
    return bool(re.match(r'^\d{5,10}$', pincode))


def validate_gst(gst):
    return bool(re.match(r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}$', gst))
