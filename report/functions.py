# -*- encoding:utf-8 -*-

from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from django.db.models import Q
from django.db.models import Min, Max
from django.core.mail import send_mail
from django.conf import settings

from domain.models import *
from report.models import *
from comments.models import *
from helper import utilities

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

def notify_overdue_schedule():
	print 'Start notify'
	today = date.today()
	
	for report in Report.objects.all():
		print 'Report: ' + report.name
		for report_project in ReportProject.objects.filter(report=report):
			project = report_project.project
			print 'Project: ' + project.name
			for user_role_responsibility in UserRoleResponsibility.objects.filter(projects=project, role__name__in=('project_manager', 'project_manager_assistant')):
				user_account = user_role_responsibility.user
				user = user_account.user
				
				# Case before due date n days
				for report_schedule in ReportSchedule.objects.filter(report_project=report_project, due_date=today+timedelta(report.notify_days), state=NO_ACTIVITY):
					print report_schedule.due_date.strftime('%d %B %Y').decode('utf-8') + ' send to ' + user.email
					
					message = u'คุณ %s มี %s ภายใต้ %s ที่ต้องส่งภายในวันที่ %s' % (
						user_account.first_name + ' ' + user_account.last_name, 
						report.name,
						project.name,
						utilities.format_date(report_schedule.due_date), 
					)
					send_mail('แจ้งเตือนการส่งรายงาน', message, 'application.testbed@gmail.com', ['crosalot@gmail.com'], fail_silently=False)
				
				# Case due date
				for report_schedule in ReportSchedule.objects.filter(report_project=report_project, due_date=today, state=NO_ACTIVITY):
					print report_schedule.due_date.strftime('%d %B %Y').decode('utf-8') + ' send to ' + user.email

					message = u'คุณ %s มี %s ภายใต้ %s ที่ต้องส่งภายในวันนี้่ %s \nถ้าเกินวันนี้ไปจะถือว่ารายงานนี้ล่าช้ากว่ากำหนด' % (
						user_account.first_name + ' ' + user_account.last_name, 
						report.name,
						project.name,
						utilities.format_date(report_schedule.due_date), 
					)
					send_mail('แจ้งเตือนการส่งรายงาน', message, 'application.testbed@gmail.com', ['crosalot@gmail.com'], fail_silently=False)