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

def get_checkup_reports(project):
	"""
	For sector manager assistant
	
	- submitted reports that need approval
	- overdue reports
	- before-due submitted reports
	"""
	report_projects = ReportProject.objects.filter(project=project, report__need_checkup=True)
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
		if report_project.is_active:
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
	
	report_projects = ReportProject.objects.filter(project=project)
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
		if report_project.is_active:
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

def notify_overdue_schedule():
	current_date = date.today()
	site = Site.objects.get_current()
	email_datatuple = list()
	
	for report in Report.objects.all():
		for report_project in ReportProject.objects.filter(report=report):
			overdue_schedules = list()
			notify_schedules = list()
			
			# Overdue
			next_date = report_project.report.schedule_start
			while next_date < current_date:
				report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
				
				if report_schedule.state == NO_ACTIVITY and report_schedule.schedule_date + timedelta(days=settings.REPORT_ALERT_AFTER) == current_date:
					overdue_schedules.append(report_schedule)
				
				next_date = _get_next_schedule(next_date, report_project.report)
			
			# Notify
			if report.notify_days:
				notify_date = current_date + timedelta(days=report.notify_days)
				while next_date < notify_date:
					next_date = _get_next_schedule(next_date, report_project.report)
					
				if next_date == notify_date:
					report_schedule, created = ReportSchedule.objects.get_or_create(report_project=report_project, schedule_date=next_date)
					
					if report_schedule.state == NO_ACTIVITY:
						notify_schedules.append(report_schedule)
			
			if notify_schedules or overdue_schedules:
				# Sending Email
				recipient_list = list()
				for user_role_responsibility in UserRoleResponsibility.objects.filter(projects=report_project.project, role__name__in=('project_manager', 'project_manager_assistant')):
					recipient_list.append(user_role_responsibility.user.user.email)
				
				email_subject = render_to_string('email/notify_report_subject.txt', {'site':site, 'project':report_project.project, 'notify_schedules':notify_schedules, 'overdue_schedules':overdue_schedules}).strip(' \n\t')
				email_message = render_to_string('email/notify_report_message.txt', {'site':site, 'project':report_project.project, 'notify_schedules':notify_schedules, 'overdue_schedules':overdue_schedules}).strip(' \n\t')
				
				email_datatuple.append((email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, recipient_list))
	
	if email_datatuple:
		send_mass_mail(email_datatuple, fail_silently=True)
