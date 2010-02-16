# -*- encoding: utf-8 -*-
import calendar
from datetime import date

from accounts.models import UserRoleResponsibility

THAI_MONTH_NAME = ('', 'มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม')
THAI_MONTH_ABBR_NAME = ('', 'ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.')

WEEKDAY_THAI_NAME = ('', 'วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์', 'วันอาทิตย์')

def format_full_datetime(datetime):
	return unicode('%d %s %d เวลา %d:%d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_abbr_datetime(datetime):
	return unicode('%d %s %d เวลา %d:%d น.', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543, datetime.hour, datetime.minute)

def format_full_date(datetime):
	return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_abbr_date(datetime):
	return unicode('%d %s %d', 'utf-8') % (datetime.day, unicode(THAI_MONTH_ABBR_NAME[datetime.month], 'utf-8'), datetime.year + 543)

def format_full_month_year(datetime):
	return "%s %d" % (unicode(THAI_MONTH_NAME[datetime.month], "utf-8"), datetime.year + 543)

def format_abbr_month_year(datetime):
	return "%s %d" % (unicode(THAI_MONTH_ABBR_NAME[datetime.month], "utf-8"), datetime.year + 543)

# Master Plan Year
def master_plan_current_year_span(master_plan):
	today = date.today()
	month_span = master_plan.month_span
	
	if month_span.start_month == 1:
		return (date(today.year, 1, 1), date(today.year, 12, 31))
	else:
		if today.month >= month_span.start_month:
			return (
				date(today.year, month_span.start_month, 1),
				date(today.year+1, month_span.start_month-1, calendar.monthrange(today.year+1, month_span.start_month-1)[1])
				)
		else:
			return (
				date(today.year-1, month_span.start_month, 1),
				date(today.year, month_span.start_month-1, calendar.monthrange(today.year, month_span.start_month-1)[1])
				)

def master_plan_current_year_number(master_plan):
	today = date.today()
	month_span = master_plan.month_span
	
	if month_span.start_month == 1:
		return today.year
	else:
		if today.month >= month_span.start_month:
			return today.year if month_span.use_lower_year_number else (today.year + 1)
		else:
			return (today.year - 1) if month_span.use_lower_year_number else today.year

# KPI and Finance Revision
def get_kpi_revised_list(revision):
	revised_list = list()
	
	if revision.org_target_on != revision.new_target_on:
		revised_list.append(unicode('วันที่คาดการณ์จากวันที่ %s เป็นวันที่ %s', 'utf-8') % (format_abbr_date(revision.org_target_on), format_abbr_date(revision.new_target_on)))
	
	if revision.org_target != revision.new_target:
		revised_list.append(unicode('ตัวเลขคาดการณ์จาก %d เป็น %d', 'utf-8') % (revision.org_target, revision.new_target))
	
	if revision.org_result != revision.new_result:
		revised_list.append(unicode('ตัวเลขผลที่เกิดขึ้นจาก %d เป็น %d', 'utf-8') % (revision.org_result, revision.new_result))
	
	return revised_list

def get_finance_revised_list(revision):
	revised_list = list()
	
	if revision.org_target_on != revision.new_target_on:
		revised_list.append(unicode('วันที่คาดการณ์จากวันที่ %s เป็นวันที่ %s', 'utf-8') % (format_abbr_date(revision.org_target_on), format_abbr_date(revision.new_target_on)))
	
	if revision.org_target != revision.new_target:
		revised_list.append(unicode('ตัวเลขการคาดการณ์จาก %d เป็น %d', 'utf-8') % (revision.org_target, revision.new_target))
	
	if revision.org_result != revision.new_result:
		revised_list.append(unicode('ตัวเลขการเบิกจ่ายจาก %d เป็น %d', 'utf-8') % (revision.org_result, revision.new_result))
	
	return revised_list

def get_kpi_revision_html(revision):
	html = unicode('<span class="timestamp">แก้ไขเมื่อ %s น.</span>', 'utf-8') % format_abbr_datetime(revision.revised_on)
	
	if revision.org_target_on != revision.new_target_on:
		html += unicode('<span>วันที่คาดการณ์จากวันที่ %s เป็นวันที่ %s</span>', 'utf-8') % (format_abbr_date(revision.org_target_on), format_abbr_date(revision.new_target_on))
	
	if revision.org_target != revision.new_target:
		html += unicode('<span>ตัวเลขคาดการณ์จาก %d เป็น %d</span>', 'utf-8') % (revision.org_target, revision.new_target)
	
	if revision.org_result != revision.new_result:
		html += unicode('<span>ตัวเลขผลที่เกิดขึ้นจาก %d เป็น %d</span>', 'utf-8') % (revision.org_result, revision.new_result)
	
	return html

def get_finance_revision_html(revision):
	html = unicode('<span class="timestamp">แก้ไขเมื่อ %s น.</span>', 'utf-8') % format_abbr_datetime(revision.revised_on)
	
	if revision.org_target_on != revision.new_target_on:
		html += unicode('<span>วันที่คาดการณ์จากวันที่ %s เป็นวันที่ %s</span>', 'utf-8') % (format_abbr_date(revision.org_target_on), format_abbr_date(revision.new_target_on))
	
	if revision.org_target != revision.new_target:
		html += unicode('<span>ตัวเลขการคาดการณ์จาก %d เป็น %d</span>', 'utf-8') % (revision.org_target, revision.new_target)
	
	if revision.org_result != revision.new_result:
		html += unicode('<span>ตัวเลขการเบิกจ่ายจาก %d เป็น %d</span>', 'utf-8') % (revision.org_result, revision.new_result)
	
	return html

# Find month
def get_prev_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	month_index = MONTH.index(month)
	prev_index = month_index - num
	if abs(prev_index) > 12:
		prev_index = 12 % prev_index

	if prev_index < 0:
		year = year + (prev_index / 12)

	return (year, MONTH[prev_index])

def get_next_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	delta = num
	index = month + num

	return (year + (index / 13), MONTH[index % 12 - 1])

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
	
	if 'admin' in roles and user.is_superuser: return True
	
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


