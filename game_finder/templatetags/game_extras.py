from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def add_class(field, class_name):
    """ Adds a class to a field.

        There appears to be a bug in css_classes() returning nothing,
        so the class_name should be the entire new class list.
    """
    return field.as_widget(attrs={
        "class": " ".join((field.css_classes(), class_name))
    })


@register.filter
def prettify_name_tuple(tup):
    """ Processes the intersect tuples from the steam API. """
    res = []
    for name in tup:
        res.append(name.split("_")[0])
    return ", ".join(res)


@register.filter
def generate_price(amount):
    """ Processes decimal prices into strings. """
    if amount == Decimal('0.0'):
        return "Free"
    elif amount == Decimal('-1.0'):
        return "??"
    else:
        return "$" + str(amount)
