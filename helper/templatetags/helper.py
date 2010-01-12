from django import template
from django.template.defaultfilters import stringfilter

from thaihealthsms.helper.utilities import format_abbr_datetime, format_datetime, format_abbr_date, format_date, format_month_year, format_display_datetime

register = template.Library()

@register.filter(name='thai_date')
def thai_date(datetime):
	return format_date(datetime)

@register.filter(name='thai_abbr_date')
def thai_abbr_date(datetime):
	return format_abbr_date(datetime)

@register.filter(name='thai_datetime')
def thai_datetime(datetime):
	return format_datetime(datetime)

@register.filter(name='thai_abbr_datetime')
def thai_abbr_datetime(datetime):
	return format_abbr_datetime(datetime)

@register.filter(name='thai_display_datetime')
def thai_display_datetime(datetime):
	return format_display_datetime(datetime)

@register.filter(name='thai_month_year')
def thai_month_year(datetime):
	return format_month_year(datetime)