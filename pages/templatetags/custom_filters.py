from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter()
def dict_lookup(dictionary, key):
    return dictionary.get(key, "")


@register.filter()
def neg_dollar(value):
    """Format a number as currency with negative sign before the dollar sign.
    e.g. -123456.78 -> -$123,457 instead of $-123,457
    """
    num = round(float(value))
    if num < 0:
        return f"-${intcomma(abs(num))}"
    return f"${intcomma(num)}"
