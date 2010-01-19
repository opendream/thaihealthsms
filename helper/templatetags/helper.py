from django import template
from django.template import NodeList
from django.template.defaultfilters import stringfilter

from thaihealthsms.helper.utilities import format_abbr_datetime, format_datetime, format_abbr_date, format_date, format_month_year, format_display_datetime
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

@register.simple_tag
def who_responsible(department):
	users = utilities_who_responsible(department)
	
	return ', '.join([user.first_name + ' ' + user.last_name for user in users])


class RoleDepartmentNode(template.Node):
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
		roles = self.roles.split(',')
		dept_obj = self.dept_obj.resolve(context)
		
		has_responsibility = False
		
		for responsibility_item in UserRoleResponsibility.objects.filter(user=user):
			if responsibility_item.role.name in roles:
				print "HAS ROLE"
				if type(dept_obj).__name__ == 'Project':
					if dept_obj in responsibility_item.projects.all():
						has_responsibility = True
				elif type(dept_obj).__name__ == 'Project':
					if dept_obj in responsibility_item.projects.all():
						has_responsibility = True
		
		if has_responsibility:
			print "[[1]]"
			output = self.nodelist_true.render(context)
			return output
		else:
			print "[[2]]"
			output = self.nodelist_false.render(context)
			return output

@register.tag(name="role_dept")
def do_role_dept(parser, token):
	try:
		tag_name, user, roles, dept_obj = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Role tag raise ValueError"
	
	nodelist_true = parser.parse(('else', 'endrole_dept'))
	token = parser.next_token()
	if token.contents == 'else':
		nodelist_false = parser.parse(('endrole_dept',))
		parser.delete_first_token()
	else:
		nodelist_false = NodeList()
	
	return RoleDepartmentNode(nodelist_true, nodelist_false, user, roles, dept_obj)


class RoleNode(template.Node):
	"""
	Template tag to display content inside {% role user 'roles' %}{% endrole %}
	if user has one of the listed roles
	
	Parameter:
	user : django.contrib.auth.user object
	roles : string represent a list of role e.g. 'sector_manager,sector_manager_assistant'
	
	"""
	
	def __init__(self, nodelist, user, roles):
		self.nodelist = nodelist
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
				output = self.nodelist.render(context)
				return output
		
		return ""

@register.tag(name="role")
def do_role(parser, token):
	try:
		tag_name, user, roles = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Role tag raise ValueError"
	
	nodelist = parser.parse(('endrole',))
	parser.delete_first_token()
	return RoleNode(nodelist, user, roles)
