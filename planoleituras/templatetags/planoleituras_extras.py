from django import template
#from django.utils.datastructures import SortedDict

register = template.Library()

@register.filter(name='sort')
def listsort(value):
	return sorted(value)
	listsort.is_safe = True

@register.filter(name='get_value_dict')
def get_value_dict(dict, key):
	return dict[key]
	get_value_dict.is_safe = True