from django import template

register = template.Library()


@register.filter
def get_range(value):
    """数値からrangeを生成するフィルター"""
    return range(1, int(value) + 1)
