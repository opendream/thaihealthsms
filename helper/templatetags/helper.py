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
				return output.upper()
		
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
