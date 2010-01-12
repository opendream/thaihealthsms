# -*- encoding:utf-8 -*-

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mail
from django.conf import settings

from domain.models import Project
from report.models import *


def get_submitted_and_overdue_reports(project): # For assistant
	report_projects = ReportProject.objects.filter(project=project)
	current_date = date.today()
	
	for report_project in report_projects:
		next_due = ReportSchedule.objects.filter(report_project=report_project, due_date__gte=current_date).aggregate(Min('due_date'))['due_date__min']
		last_due = ReportSchedule.objects.filter(report_project=report_project, due_date__lt=current_date).aggregate(Max('due_date'))['due_date__max']
		
		schedules = ReportSchedule.objects.filter(report_project=report_project).filter((Q(is_submitted=False) & Q(due_date__lt=current_date)) | Q(due_date=last_due) | (Q(due_date=next_due) & Q(is_submitted=True))).order_by('-due_date')
		
		for schedule in schedules: schedule.overdue = schedule.due_date < current_date and not schedule.is_submitted
		report_project.schedules = schedules
	
	return report_projects

def get_nextdue_and_overdue_reports(project): # For project manager
	report_projects = ReportProject.objects.filter(project=project)
	current_date = date.today()
	
	for report_project in report_projects:
		next_due = ReportSchedule.objects.filter(report_project=report_project, due_date__gte=current_date).aggregate(Min('due_date'))['due_date__min']
		
		schedules = ReportSchedule.objects.filter(report_project=report_project).filter((Q(is_submitted=False) & Q(due_date__lt=current_date)) | Q(due_date=next_due)).order_by('-due_date')
		
		for schedule in schedules: schedule.overdue = schedule.due_date < current_date and not schedule.is_submitted
		report_project.schedules = schedules
	
	return report_projects

def notify_due_report():
	today = date.today()
	# Case before due date n days
	report_schedule = ReportSchedule.objects.filter(due_date=today.replace(day=today.day+settings.REPORT_DAYS_ALERT))
	text = u'คุณ %s มี %s ภายใต้ %s ที่ต้องส่งภายในวันที่ %s'
	send_mail_to_pm(report_schedule, text)
	
	# Case due date
	report_schedule = ReportSchedule.objects.filter(due_date=today)
	text = u'คุณ %s มี %s ภายใต้ %s ที่ต้องส่งภายในวันนี้ %s'
	send_mail_to_pm(report_schedule, text)

def send_mail_to_pm(report_schedule, text):
	for rep in report_schedule:
		project = rep.report_project.project
		manager = project.manager
		email = manager.user.email
		
		# Variable use for email
		full_name = manager.first_name + ' ' + manager.last_name
		project_name = project.name
		report_name = rep.report_project.report.name
		before_n_day = settings.REPORT_DAYS_ALERT
		due_date = rep.due_date.strftime('%d %B %Y').decode('utf-8')
		
		message = text % (full_name, report_name, project_name, due_date)
		
		send_mail('แจ้งเตือนการส่งรายงาน', message, 'smtp.gmail.com', [email])


