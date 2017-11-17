from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def add_class(field, class_name):
    return field.as_widget(attrs={
        "class": " ".join((field.css_classes(), class_name))
    })


@register.filter
def prettify_name_tuple(tup):
    res = []
    for name in tup:
        res.append(name.split("_")[0])
    return ", ".join(res)


@register.filter
def generate_price(amount):
    if amount == Decimal('0.0'):
        return "Free"
    elif amount == Decimal('-1.0'):
        return "??"
    else:
        return "$" + str(amount)
