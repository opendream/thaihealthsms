# -*- encoding:utf-8 -*-

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mail
from django.conf import settings

from domain.models import Project
from report.models import *
from comments.models import *

def get_submitted_and_overdue_reports(project):
	"""
	For sector manager assistant
	
	- submitted reports that need approval
	- overdue reports
	- before-due submitted reports
	"""
	report_projects = ReportProject.objects.filter(project=project, report__need_checkup=True)
	current_date = date.today()
	
	for report_project in report_projects:
		
		schedules = ReportSchedule.objects \
			.filter(report_project=report_project) \
			.filter((Q(report_project__report__need_approval=True) & Q(state=SUBMIT_ACTIVITY)) | (Q(state=NO_ACTIVITY) & Q(due_date__lt=current_date)) | Q(state=REJECT_ACTIVITY) | (Q(due_date__gte=current_date) & Q(state=SUBMIT_ACTIVITY))) \
			.exclude(state=CANCEL_ACTIVITY).order_by('-due_date')
		
		for schedule in schedules:
			schedule.need_approval = schedule.report_project.report.need_approval and schedule.state == SUBMIT_ACTIVITY
			schedule.overdue = schedule.state == NO_ACTIVITY
				
		report_project.schedules = schedules

	return report_projects

def get_nextdue_and_overdue_reports(project):
	"""
	For project manager
	- Next due reports
	- Rejected reports
	- Overdue reports
	"""
	
	report_projects = ReportProject.objects.filter(project=project)
	current_date = date.today()
	
	for report_project in report_projects:
		next_due = ReportSchedule.objects.filter(report_project=report_project, due_date__gte=current_date).aggregate(Min('due_date'))['due_date__min']
		
		schedules = ReportSchedule.objects \
			.filter(report_project=report_project) \
			.filter((Q(state=NO_ACTIVITY) & Q(due_date__lt=current_date)) | Q(state=REJECT_ACTIVITY) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_approval=True)) | (Q(due_date=next_due) & Q(state=NO_ACTIVITY))).order_by('-due_date')

		for schedule in schedules:
			schedule.waiting = schedule.state == SUBMIT_ACTIVITY
			schedule.rejected = schedule.state == REJECT_ACTIVITY
			
			schedule.overdue = schedule.state == NO_ACTIVITY
			if schedule.overdue: schedule.overdue_period = (current_date - schedule.due_date).days
			
			
		report_project.schedules = schedules

	return report_projects

def get_schedule_statuses(schedule):
	current_date = date.today()

	statuses = []
	if schedule.due_date >= current_date:
		statuses.append('nextdue')
	if schedule.due_date < current_date and not schedule.is_submitted:
		statuses.append('overdue')
	if schedule.is_submitted:
		statuses.append('submitted')
	if schedule.last_activity == APPROVE_ACTIVITY:
		statuses.append('approved')
	if schedule.last_activity == REJECT_ACTIVITY:
		statuses.append('rejected')

	return statuses

def get_all_reports_schedule_by_project(project):
	report_projects = ReportProject.objects.filter(project=project)
	current_date = date.today()

	for report_project in report_projects:
		report = report_project.report
		schedules = ReportSchedule.objects.filter(report_project=report_project)
		report_project.schedules = schedules.order_by('-due_date')[:5]
		for schedule in report_project.schedules:
			statuses = get_schedule_statuses(schedule)
			schedule.statuses = ' '.join(statuses)
			if 'overdue' in statuses:
				schedule.late_ago = (current_date - schedule.due_date).days

			schedule.comment_count = Comment.objects.filter(object_id=schedule.id, object_name="report").count()

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
