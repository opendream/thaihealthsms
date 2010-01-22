# -*- encoding: utf-8 -*-

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

# Current Year
from datetime import date
from domain.models import MasterPlanYear

def what_is_current_year(master_plan):
	today = date.today().replace(day=1)
	return MasterPlanYear.objects.get(master_plan=master_plan, start_month__lte=today, end_month__gte=today)

# Roles
def user_has_role(user, roles):
	user_groups = user.groups.all()
	
	if user_groups:
		user_roles = set([group.name for group in user_groups])
		roles = set(roles)
		
		if user_roles.intersection(roles): return True
	
	return False

# Who responsible
from domain.models import UserRoleResponsibility

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

def set_message(request, text, status='message'):
	if len(request.session.get('messages', [])) == 0:
		request.session['messages'] = []
	request.session['messages'].append({'text': text, 'class': status})
