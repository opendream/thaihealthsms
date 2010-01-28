# -*- encoding: utf-8 -*-
from datetime import date

from domain.models import MasterPlanMonthPeriod
from domain.models import UserRoleResponsibility
import calendar

THAI_MONTH_NAME = ('', 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม')
THAI_MONTH_ABBR_NAME = ('', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.')

WEEKDAY_THAI_NAME = ('', 'วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์', 'วันอาทิตย์')

def format_display_datetime(datetime):
	return "%d %s %d" % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543) + unicode(" เวลา ", "utf-8") + "%02d:%02d" % (datetime.hour, datetime.minute) + unicode(" น.", "utf-8")

def format_abbr_datetime(datetime):
	return "%d %s %d %02d:%02d" % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543, datetime.hour, datetime.minute)

def format_datetime(datetime):
	return "%d %s %d %02d:%02d" % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543, datetime.hour, datetime.minute)

def format_abbr_date(datetime):
	return "%d %s %d" % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_date(datetime):
	return "%d %s %d" % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_month_year(datetime):
	return "%s %d" % (unicode(THAI_MONTH_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_abbr_month_year(datetime):
	return "%s %d" % (unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543)

# Current Year
def current_year_number():
	today = date.today().replace(day=1)
	month_period = MasterPlanMonthPeriod.objects.get(is_default=True)

	if month_period.start_month == 1 and month_period.end_month == 12:
		current_year = today.year
	else:
		if today.month >= month_period.start_month:
			current_year = today.year if month_period.use_lower_year_number else (today.year + 1)
		else:
			current_year = (today.year - 1) if month_period.use_lower_year_number else today.year

	return current_year

# Password Generator
allow_password_chars = '0123456789'
random_password_length = 6
def make_random_user_password():
	from random import choice
	return ''.join([choice(allow_password_chars) for i in range(random_password_length)])

# Roles
def user_has_role(user, roles):
	user_groups = user.groups.all()
	roles = roles.split(',')

	if user_groups:
		user_roles = set([group.name for group in user_groups])
		roles = set(roles)

		if user_roles.intersection(roles): return True

	return False

def responsible(user, roles, dept_obj):
	has_responsibility = False
	roles = roles.split(',')
	
	for responsibility_item in UserRoleResponsibility.objects.filter(user=user):
		if responsibility_item.role.name in roles:
			if type(dept_obj).__name__ == 'Sector':
				if dept_obj in responsibility_item.sectors.all():
					has_responsibility = True
				
				if user.get_profile().sector.id == dept_obj.id:
					has_responsibility = True
				
			elif type(dept_obj).__name__ == 'Project':
				if dept_obj in responsibility_item.projects.all():
					has_responsibility = True

	return has_responsibility

# Who responsible
def who_responsible(department):
	if type(department).__name__ == 'Sector':
		responsibility = UserRoleResponsibility.objects.filter(role__name='sector_manager', sectors__in=(department,))

	elif type(department).__name__ == 'Project':
		responsibility = UserRoleResponsibility.objects.filter(role__name='project_manager', projects__in=(department,))
		if not responsibility: responsibility = UserRoleResponsibility.objects.filter(role__name='project_manager', plans__in=(department.plan,))

	users = list()
	for responsibility_item in responsibility:
		users.append(responsibility_item.user)

	return users

def schedule_month_date(report, year, month):
	'''
	Return datetime.date object of ReportSchedule due date
	of specific month and year
	'''

	day = report.schedule_monthly_date
	first_day, last_day = calendar.monthrange(year, month)
	if day == 0 or day > last_day:
		day = last_day

	return date(year, month, day)

def set_message(request, text, status='message'):
	if len(request.session.get('messages', [])) == 0:
		request.session['messages'] = []
	request.session['messages'].append({'text': text, 'class': status})
