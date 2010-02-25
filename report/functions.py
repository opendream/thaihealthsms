# -*- encoding:utf-8 -*-
import calendar
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mass_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.conf import settings

from accounts.models import *
from domain.models import *
from report.models import *
from comments.models import *
from helper import utilities

# For creating report
def generate_report_schedule_start(start_now, schedule_monthly_date):
	current_date = date.today()
	first_day, last_day = calendar.monthrange(current_date.year, current_date.month)
	
	schedule_monthly_date = int(schedule_monthly_date)
	
	if schedule_monthly_date == 0: schedule_monthly_date = last_day
	
	if start_now:
		schedule_start = date(current_date.year, current_date.month, schedule_monthly_date)
	else:
		if current_date.month == 12:
			schedule_start = date(current_date.year+1, 1, schedule_monthly_date)
		else:
			schedule_start = date(current_date.year, current_date.month+1, schedule_monthly_date)
	
	return schedule_start

"""
def get_report_due_date(report, year, month): # Not use?
	
	#Provide report object, month and year
	#Return supposedly due date for that month and year

	day = report.schedule_monthly_date
	first_day, last_day = calendar.monthrange(year, month)
	if day == 0 or day > last_day:
		day = last_day

	return date(year, month, day)
"""

def get_checkup_reports(project):
	"""
	For sector manager assistant
	
	- submitted reports that need approval
	- overdue reports
	- before-due submitted reports
	"""
	report_projects = ReportProject.objects.filter(project=project, report__need_checkup=True, is_active=True)
	current_date = date.today()
	
	has_schedules = False
	
	for report_project in report_projects:
		schedules = list()
		
		# Overdue + Waiting
		next_date = report_project.report.schedule_start
		while next_date < current_date:
			report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
			
			if report_schedule.state == NO_ACTIVITY or report_schedule.state == REJECT_ACTIVITY or (report_schedule.state == SUBMIT_ACTIVITY and report_project.report.need_approval):
				schedules.append(report_schedule)
			
			next_date = _get_next_schedule(next_date, report_project.report)
		
		# Nextdue
		report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
		
		if report_schedule.state == SUBMIT_ACTIVITY:
			schedules.append(report_schedule)
		
		if schedules: has_schedules = True
		
		for schedule in schedules:
			schedule.need_approval = schedule.report_project.report.need_approval and schedule.state == SUBMIT_ACTIVITY
			schedule.overdue = schedule.state == NO_ACTIVITY and schedule.schedule_date < current_date
		
		schedules.reverse()
		report_project.schedules = schedules
	
	if not has_schedules:
		return list()
	
	return report_projects

def get_sending_reports(project):
	"""
	For project manager
	- Next due reports
	- Rejected reports
	- Overdue reports
	- Waiting approval
	"""
	
	report_projects = ReportProject.objects.filter(project=project, is_active=True)
	current_date = date.today()
	
	for report_project in report_projects:
		schedules = list()
		
		# Overdue + Rejected + Waiting
		next_date = report_project.report.schedule_start
		while next_date < current_date:
			report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
			
			if report_schedule.state == NO_ACTIVITY or report_schedule.state == REJECT_ACTIVITY or (report_schedule.state == SUBMIT_ACTIVITY and report_project.report.need_approval):
				schedules.append(report_schedule)
			
			next_date = _get_next_schedule(next_date, report_project.report)
		
		# Nextdue
		report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
		
		if report_schedule.state == NO_ACTIVITY:
			schedules.append(report_schedule)
		
		for schedule in schedules:
			schedule.waiting = schedule.state == SUBMIT_ACTIVITY
			schedule.rejected = schedule.state == REJECT_ACTIVITY
			schedule.overdue = schedule.state == NO_ACTIVITY and schedule.schedule_date < current_date
		
		schedules.reverse()
		report_project.schedules = schedules

	return report_projects

def _get_nextdue_schedule(report):
	current_date = date.today()
	
	next_date = report.schedule_start
	while next_date < current_date:
		next_date = _get_next_schedule(next_date, report)
	
	return next_date

def _get_next_schedule(current_schedule, report):
	month = current_schedule.month + report.schedule_cycle_length
	
	if month > 12:
			month = month - 12
			year = current_schedule.year + 1
	else:
		year = current_schedule.year
	
	if report.schedule_monthly_date == 0:
		first_day, last_day = calendar.monthrange(year, month)
		day = last_day
	else:
		day = current_schedule.day
	
	return date(year, month, day)

def get_schedule_statuses(schedule):
	current_date = date.today()

	statuses = []
	if schedule.schedule_date >= current_date:
		statuses.append('nextdue')
	if schedule.schedule_date < current_date and not schedule.is_submitted:
		statuses.append('overdue')
	if schedule.is_submitted:
		statuses.append('submitted')
	if schedule.last_activity == APPROVE_ACTIVITY:
		statuses.append('approved')
	if schedule.last_activity == REJECT_ACTIVITY:
		statuses.append('rejected')

	return statuses

"""
def get_all_reports_schedule_by_project(project): # Not use?
	report_projects = ReportProject.objects.filter(project=project)
	current_date = date.today()

	for report_project in report_projects:
		report = report_project.report
		schedules = ReportSchedule.objects.filter(report_project=report_project)
		report_project.schedules = schedules.order_by('-schedule_date')[:5]
		for schedule in report_project.schedules:
			statuses = get_schedule_statuses(schedule)
			schedule.statuses = ' '.join(statuses)
			if 'overdue' in statuses:
				schedule.late_ago = (current_date - schedule.schedule_date).days

			schedule.comment_count = Comment.objects.filter(object_id=schedule.id, object_name="report").count()

	return report_projects
"""

def notify_overdue_schedule():
	today = date.today()
	site = Site.objects.get_current()
	email_datatuple = list()
	
	for report in Report.objects.all():
		for report_project in ReportProject.objects.filter(report=report):
			# Overdue
			overdue_schedules = list()
			
			next_date = report_project.report.schedule_start
			while next_date < current_date:
				report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
				
				if report_schedule.state == NO_ACTIVITY:
					overdue_schedules.append(report_schedule)
				
				next_date = _get_next_schedule(next_date, report_project.report)
			
			# Notify
			notify_schedules = list()
			
			notify_date = next_date + timedelta(days=report.notify_days)
			while next_date < notify_date:
				next_date = _get_next_schedule(next_date, report_project.report)
			
			if next_date == notify_date:
				report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_due)
				
				if report_schedule.state == NO_ACTIVITY:
					notify_schedules.append(report_schedule)
			
			# Sending Email
			recipient_list = list()
			for user_role_responsibility in UserRoleResponsibility.objects.filter(projects=report_project.project, role__name__in=('project_manager', 'project_manager_assistant')):
				recipient_list.append(user_role_responsibility.user.user.email)
			
			email_subject = render_to_string('email/notify_report_subject.txt', {site:site, project:report_project.project, notify_schedules:notify_schedules, overdue_schedules:overdue_schedules}).strip(' \n\t')
			email_message = render_to_string('email/notify_report_message.txt', {site:site, project:report_project.project, schedules:schedules, overdue_schedules:overdue_schedules}).strip(' \n\t')
			
			email_datatuple.append((email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, recipient_list))
	
	send_mass_mail(email_datatuple, fail_silently=True)
	
	
	
	"""
	for report in Report.objects.all():
		#print 'Report: ' + report.name
		for report_project in ReportProject.objects.filter(report=report):
			project = report_project.project
			#print 'Project: ' + project.name
			for user_role_responsibility in UserRoleResponsibility.objects.filter(projects=project, role__name__in=('project_manager', 'project_manager_assistant')):
				user_account = user_role_responsibility.user
				user = user_account.user
				
				report_schedules = list()
				
				# Case due date
				for report_schedule in ReportSchedule.objects.filter(report_project=report_project, schedule_date=today, state=NO_ACTIVITY):
					#print report_schedule.schedule_date.strftime('%d %B %Y').decode('utf-8') + ' send to ' + user.email
					if not users_mail.get(user.id):
						users_mail[user.id] = {
							'user_account': user_account, 
							'site':Site.objects.get_current(),
							'due_report_schedules': list(),
							'nextdue_report_schedules': list(),
						}
					users_mail[user.id]['due_report_schedules'].append(report_schedule)
					
				# Case before due date n days
				for report_schedule in ReportSchedule.objects.filter(report_project=report_project, schedule_date=today+timedelta(report.notify_days), state=NO_ACTIVITY):
					#print report_schedule.schedule_date.strftime('%d %B %Y').decode('utf-8') + ' send to ' + user.email
					if not users_mail.get(user.id):
						users_mail[user.id] = {
							'user_account': user_account, 
							'site':Site.objects.get_current(),
							'due_report_schedules': list(),
							'nextdue_report_schedules': list(),
						}
					users_mail[user.id]['nextdue_report_schedules'].append(report_schedule)
	
	datatuple = list()
	for user_id, user_mail in users_mail.items():
		email_recipient_list = [user_mail.user_account.user.email]
		
		email_subject = render_to_string('email/notify_report_subject.txt', user_mail).strip(' \n\t')
		email_message = render_to_string('email/notify_report_message.txt', user_mail).strip(' \n\t')
		
		datatuple.append((email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, email_recipient_list))
	"""
	
