# -*- encoding: utf-8 -*-

from django import template
from django.template import NodeList
from django.template.defaultfilters import stringfilter

from thaihealthsms.helper.utilities import format_abbr_datetime, format_datetime, format_abbr_date, format_date, format_month_year, format_display_datetime
from thaihealthsms.helper.utilities import responsible as utilities_responsible
from thaihealthsms.helper.utilities import who_responsible as utilities_who_responsible

from domain.models import UserRoleResponsibility

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

from datetime import date

@register.filter(name='elapse')
def elapse(value):
	current_date = date.today()
	
	days_elapse = (current_date - value).days
	weeks_elapse = 0
	
	while days_elapse >= 7:
		weeks_elapse = weeks_elapse + 1
		days_elapse = days_elapse - 7
	
	if weeks_elapse:
		if days_elapse:
			text = unicode('%d สัปดาห์ %d วัน', 'utf-8') % (weeks_elapse, days_elapse)
		else:
			text = unicode('%d สัปดาห์', 'utf-8') % weeks_elapse
		
	else:
		text = unicode('%d วัน', 'utf-8') % days_elapse
	
	return text

#
# ROLE UTILITIES FUNCTIONS
#

@register.simple_tag
def who_responsible(department):
	users = utilities_who_responsible(department)
	
	if users:
		return ', '.join([user.first_name + ' ' + user.last_name for user in users])
	else:
		return unicode('ไม่มีผู้รับผิดชอบ', 'utf-8')

from django.contrib.auth.models import Group

class IfAdminNode(template.Node):
	"""
	Check if user is an admin (system admin or sector admin)
	"""
	def __init__(self, nodelist_true, nodelist_false, user):
		self.nodelist_true = nodelist_true
		self.nodelist_false = nodelist_false
		self.user = template.Variable(user)
    
	def render(self, context):
		user = self.user.resolve(context)
		
		is_admin = False
		
		if user.is_superuser:
			is_admin = True
			
		else:
			if Group.objects.get(name='sector_admin') in user.groups.all():
				is_admin = True
		
		if is_admin:
			output = self.nodelist_true.render(context)
		else:
			output = self.nodelist_false.render(context)
		
		return output

@register.tag(name="ifadmin")
def do_ifadmin(parser, token):
	try:
		tag_name, user = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "ifadmin tag raise ValueError"
	
	nodelist_true = parser.parse(('else', 'endifadmin'))
	token = parser.next_token()
	if token.contents == 'else':
		nodelist_false = parser.parse(('endifadmin',))
		parser.delete_first_token()
	else:
		nodelist_false = NodeList()
	
	return IfAdminNode(nodelist_true, nodelist_false, user)


class ResponsibleNode(template.Node):
	"""
	Template tag to display content inside {% role user 'roles' %}{% endrole %}
	if user has one of the listed roles
	
	Parameter:
	user : django.contrib.auth.user object
	roles : string represent a list of role e.g. 'sector_manager,sector_manager_assistant'
	project_id : 
	"""
	
	def __init__(self, nodelist_true, nodelist_false, user, roles, dept_obj):
		self.nodelist_true = nodelist_true
		self.nodelist_false = nodelist_false
		self.user = template.Variable(user)
		self.roles = roles.strip(' \"\'')
		self.dept_obj = template.Variable(dept_obj)
    
	def render(self, context):
		user = self.user.resolve(context)
		roles = self.roles
		dept_obj = self.dept_obj.resolve(context)
		
		if utilities_responsible(user, roles, dept_obj):
			output = self.nodelist_true.render(context)
			return output
		else:
			output = self.nodelist_false.render(context)
			return output

@register.tag(name="responsible")
def do_responsible(parser, token):
	try:
		tag_name, user, roles, dept_obj = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Responsible tag raise ValueError"
	
	nodelist_true = parser.parse(('else', 'endresponsible'))
	token = parser.next_token()
	if token.contents == 'else':
		nodelist_false = parser.parse(('endresponsible',))
		parser.delete_first_token()
	else:
		nodelist_false = NodeList()
	
	return ResponsibleNode(nodelist_true, nodelist_false, user, roles, dept_obj)


class RoleNode(template.Node):
	"""
	Template tag to display content inside {% role user 'roles' %}{% endrole %}
	if user has one of the listed roles
	
	Parameter:
	user : django.contrib.auth.user object
	roles : string represent a list of role e.g. 'sector_manager,sector_manager_assistant'
	
	"""
	
	def __init__(self, nodelist_true, nodelist_false, user, roles):
		self.nodelist_true = nodelist_true
		self.nodelist_false = nodelist_false
		self.user = template.Variable(user)
		self.roles = roles.strip(' \"\'')
    
	def render(self, context):
		user = self.user.resolve(context)
		user_groups = user.groups.all()
		
		if user_groups:
			user_roles = set([group.name for group in user_groups])
			
			roles = self.roles.split(',')
			for role in roles: role = role.strip()
			roles = set(roles)
			
			if user_roles.intersection(roles):
				output = self.nodelist_true.render(context)
				return output
		
		output = self.nodelist_false.render(context)
		return output

@register.tag(name="role")
def do_role(parser, token):
	try:
		tag_name, user, roles = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Role tag raise ValueError"
	
	nodelist_true = parser.parse(('else', 'endrole'))
	token = parser.next_token()
	if token.contents == 'else':
		nodelist_false = parser.parse(('endrole',))
		parser.delete_first_token()
	else:
		nodelist_false = NodeList()
	
	return RoleNode(nodelist_true, nodelist_false, user, roles)
