# -*- encoding: utf-8 -*-

from datetime import datetime, date
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from accounts.models import *
from comments.models import *
from domain.models import *

from report import functions as report_functions

from helper import utilities
from helper.message import set_message
from helper.shortcuts import render_response, access_denied

#
# SECTOR REPORT
#

@login_required
def view_sector_manage_reports(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)

	reports = Report.objects.filter(sector=sector).order_by('created')

	for report in reports:
		report.project_count = ReportProject.objects.filter(report=report).count()

	return render_response(request, "page_sector/sector_manage_reports.html", {'sector':sector, 'reports':reports})

@login_required
def view_sector_add_report(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)

	if request.method == 'POST':
		form = SectorReportForm(request.POST)
		if form.is_valid():
			report_name = form.cleaned_data['name']
			need_approval = form.cleaned_data['need_approval']
			schedule_cycle_length = form.cleaned_data['schedule_cycle_length']
			start_now = form.cleaned_data['start_now']
			schedule_monthly_date = form.cleaned_data['schedule_monthly_date']
			notify_days = form.cleaned_data['notify_days']
			
			schedule_start = report_functions.generate_report_schedule_start(start_now, schedule_monthly_date)
			Report.objects.create(name=report_name, need_approval=need_approval, need_checkup=True, schedule_start=schedule_start, schedule_cycle_length=schedule_cycle_length, schedule_monthly_date=schedule_monthly_date, sector=sector, created_by=request.user.get_profile(), notify_days=notify_days)
			
			set_message(request, u'สร้างรายงานเรียบร้อย')

			return redirect('view_sector_manage_reports', (sector.id))

	else:
		form = SectorReportForm(initial={'start_now':True})

	return render_response(request, "page_sector/sector_manage_add_report.html", {'sector':sector, 'form':form})

@login_required
def view_sector_edit_report(request, report_id):
	report = get_object_or_404(Report, pk=report_id)
	sector = report.sector
	if not sector: raise Http404

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)

	if request.method == 'POST':
		form = SectorReportForm(request.POST)
		if form.is_valid():
			report.name = form.cleaned_data['name']
			report.need_approval = form.cleaned_data['need_approval']
			report.schedule_cycle_length = form.cleaned_data['schedule_cycle_length']
			report.schedule_monthly_date = form.cleaned_data['schedule_monthly_date']
			report.notify_days = form.cleaned_data['notify_days']
			report.save()
			
			set_message(request, u'แก้ไขรายงานเรียบร้อย')
			return redirect('view_sector_manage_reports', (sector.id))

	else:
		form = SectorReportForm(initial={'name':report.name, 'need_approval':report.need_approval, 'schedule_cycle_length':report.schedule_cycle_length, 'schedule_monthly_date':report.schedule_monthly_date, 'notify_days': report.notify_days})

	return render_response(request, "page_sector/sector_manage_edit_report.html", {'sector':sector, 'form':form})

@login_required
def view_sector_delete_report(request, report_id):
	report = get_object_or_404(Report, pk=report_id)
	sector = report.sector
	if not sector: raise Http404

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	project_count = ReportProject.objects.filter(report=report).count()
	if not project_count:
		report.delete()
		set_message(request, u'ลบรายงานเรียบร้อย')
	else:
		set_message(request, u'ไม่สามารถลบรายงานได้เนื่องจากมีแผนงานที่ส่งรายงานนี้อยู่')

	return redirect('view_sector_manage_reports', (sector.id))

@login_required
def view_sector_edit_project_reports(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	sector = project.master_plan.sector
	today = date.today()
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	project = get_object_or_404(Project, pk=project_id)
	
	if request.method == 'POST':
		form = MasterPlanProjectReportsForm(request.POST, sector=sector)
		if form.is_valid():
			report_before = [report_project.report for report_project in ReportProject.objects.filter(project=project, is_active=True)]
			report_after = form.cleaned_data['reports']
			
			cancel_reports = set(report_before) - set(report_after)
			
			# Cancel Reports
			for cancel_report in cancel_reports:
				# Delete report schedules that has no activities
				report_project = ReportProject.objects.get(report=cancel_report, project=project)
				ReportSchedule.objects.filter(report_project=report_project, state=NO_ACTIVITY).delete()
				report_project.is_active = False
				report_project.save()
			
			# Add New Reports
			new_reports = set(report_after) - set(report_before)
			for new_report in new_reports:
				report_project, created = ReportProject.objects.get_or_create(report=new_report, project=project)
			
			set_message(request, u'เลือกรายงานเรียบร้อย')
			return redirect('view_sector_edit_project_reports', (project.id))
		
	else:
		form = MasterPlanProjectReportsForm(sector=sector, initial={'reports':[report_project.report.id for report_project in ReportProject.objects.filter(project=project, is_active=True)]})
	
	has_reports = Report.objects.filter(sector=sector).count() > 0
	return render_response(request, 'page_sector/sector_manage_edit_project_reports.html', {'sector':sector, 'project':project, 'form':form, 'has_reports':has_reports})

#
# PROJECT REPORT
#
@login_required
def view_project_reports(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	
	report_projects = ReportProject.objects.filter(project=project)
	
	for report_project in report_projects:
		if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
			report_project.schedules = ReportSchedule.objects.filter(report_project=report_project).filter(Q(state=SUBMIT_ACTIVITY) | Q(state=APPROVE_ACTIVITY) | Q(state=REJECT_ACTIVITY)).order_by('-schedule_date')
		else:
			report_project.schedules = ReportSchedule.objects.filter(report_project=report_project).filter(Q(state=APPROVE_ACTIVITY) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_approval=False)) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_checkup=False))).order_by('-schedule_date')
		
		year_list = set()
		for schedule in report_project.schedules: year_list.add(schedule.schedule_date.year)
		year_list = sorted(year_list, reverse=True)
		
		report_project.year_list = year_list
	
	return render_response(request, "page_project/project_reports.html", {'project':project, 'report_projects':report_projects})

@login_required
def view_project_reports_manage(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if not utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	report_projects = ReportProject.objects.filter(project=project)

	sector_reports = list()
	project_reports = list()

	for report_project in report_projects:
		if report_project.report.sector:
			sector_reports.append(report_project.report)
		else:
			report = report_project.report
			report.is_active = report_project.is_active
			project_reports.append(report)

	return render_response(request, "page_project/project_reports_manage.html", {'project':project, 'sector_reports':sector_reports, 'project_reports':project_reports})

@login_required
def view_project_set_report_inactive(request, project_id, report_id):
	project = get_object_or_404(Project, pk=project_id)
	report = get_object_or_404(Report, pk=report_id)
	
	report_project = ReportProject.objects.get(project=project, report=report)
	report_project.is_active = False
	report_project.save()
	
	return redirect('view_project_reports_manage', (project.id))

@login_required
def view_project_reports_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if not utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	if request.method == 'POST':
		form = ProjectReportForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			need_checkup = form.cleaned_data['need_checkup']
			need_approval = form.cleaned_data['need_approval']
			schedule_cycle_length = form.cleaned_data['schedule_cycle_length']
			start_now = form.cleaned_data['start_now']
			schedule_monthly_date = form.cleaned_data['schedule_monthly_date']
			notify_days = form.cleaned_data['notify_days']
			
			schedule_start = report_functions.generate_report_schedule_start(start_now, schedule_monthly_date)
			report = Report.objects.create(
				name=name,
				need_approval=need_approval,
				need_checkup=need_checkup,
				schedule_start=schedule_start,
				schedule_cycle_length=schedule_cycle_length,
				schedule_monthly_date=schedule_monthly_date,
				created_by=request.user.get_profile(),
				notify_days=notify_days)
			
			ReportProject.objects.create(report=report, project=project)
			
			set_message(request, u"สร้างรายงานเรียบร้อย")
			return redirect('view_project_reports_manage', (project_id))

	else:
		form = ProjectReportForm(initial={'start_now':True})

	return render_response(request, "page_project/project_reports_add.html", {'project':project, 'form':form})

@login_required
def view_project_report_edit(request, project_id, report_id):
	project = get_object_or_404(Project, pk=project_id)
	report = get_object_or_404(Report, pk=report_id)

	if not utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	if request.method == 'POST':
		form = ProjectReportForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			need_checkup = form.cleaned_data['need_checkup']
			need_approval = form.cleaned_data['need_approval']
			schedule_cycle_length = form.cleaned_data['schedule_cycle_length']
			schedule_monthly_date = form.cleaned_data['schedule_monthly_date']
			notify_days = form.cleaned_data['notify_days']

			report.name = name
			report.need_checkup = need_checkup
			report.need_approval = need_approval
			report.schedule_cycle_length = schedule_cycle_length
			report.schedule_monthly_date = schedule_monthly_date
			report.notify_days = notify_days
			report.save()

			set_message(request, u"แก้ไขรายงานเรียบร้อย")
			return redirect('view_project_reports_manage', (project_id))
	else:
		form = ProjectReportForm(initial={'name':report.name, 'need_checkup':report.need_checkup, 'need_approval':report.need_approval, 'schedule_cycle_length':report.schedule_cycle_length, 'schedule_monthly_date':report.schedule_monthly_date, 'notify_days': report.notify_days})

	return render_response(request, "page_project/project_reports_edit.html", {'project':project, 'form':form})

@login_required
def view_project_reports_send(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	reports = report_functions.get_sending_reports(project_id)

	if not utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	for report in reports:
		for schedule in report.schedules:
			schedule.comment_count = Comment.objects.filter(object_name='report', object_id=schedule.id).count()

	return render_response(request, "page_project/project_reports_send.html", {'project':project, 'reports':reports})

#
# REPORT
#
@login_required
def view_report_overview(request, report_id):
	report_schedule = get_object_or_404(ReportSchedule, pk=report_id)

	if request.method == 'POST':
		project = report_schedule.report_project.project

		if not utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
			return redirect('view_report_overview', (report_schedule.id))

		submit_type = request.POST.get('submit')

		if submit_type == 'submit-file':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)

			file_response = ReportScheduleFileResponse.objects.create(schedule=schedule, uploaded_by=request.user.get_profile())

			# Uploading directory
			uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, schedule.report_project.report.id, schedule.id)
			if not os.path.exists(uploading_directory): os.makedirs(uploading_directory)

			# Uploading file
			uploading_file = request.FILES['uploading_file']
			(file_name, separator, file_ext) = uploading_file.name.rpartition('.')

			unique_filename = '%s.%s' % (file_name, file_ext)
			if os.path.isfile('%s%s' % (uploading_directory, unique_filename)):
				# Duplicated filename
				suffix_counter = 1

				while os.path.isfile('%s%s(%d).%s' % (uploading_directory, file_name, suffix_counter, file_ext)):
					suffix_counter = suffix_counter + 1

				unique_filename = '%s(%d).%s' % (file_name, suffix_counter, file_ext)

			file_response.filename = unique_filename
			file_response.save()

			destination = open(uploading_directory + unique_filename, 'wb')
			for chunk in request.FILES['uploading_file'].chunks(): destination.write(chunk)
			destination.close()

		elif submit_type == 'submit-text':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)

			text = request.POST.get("text")

			try:
				text_response = ReportScheduleTextResponse.objects.get(schedule=schedule)

			except ReportScheduleTextResponse.DoesNotExist:
				text_response = ReportScheduleTextResponse.objects.create(schedule=schedule, submitted_by=request.user.get_profile())

			text_response.text = text
			text_response.save()

		elif submit_type == 'submit-report':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)
			
			from datetime import datetime

			schedule.state = SUBMIT_ACTIVITY
			schedule.submitted_on = datetime.now()
			schedule.approval_on = None
			schedule.save()

		return redirect('/report/%d/' % schedule.id)

	current_date = date.today()

	if report_schedule.state == NO_ACTIVITY and report_schedule.schedule_date < current_date:
		report_schedule.status_code = 'overdue'
	elif report_schedule.state == NO_ACTIVITY:
		report_schedule.status_code = 'not_submitted'
	elif report_schedule.state == SUBMIT_ACTIVITY and not report_schedule.report_project.report.need_approval:
		report_schedule.status_code = 'submitted'
	elif report_schedule.state == SUBMIT_ACTIVITY and report_schedule.report_project.report.need_approval:
		report_schedule.status_code = 'waiting'
	elif report_schedule.state == APPROVE_ACTIVITY:
		report_schedule.status_code = 'approved'
	elif report_schedule.state == REJECT_ACTIVITY:
		report_schedule.status_code = 'rejected'

	report_schedule.allow_modifying = report_schedule.status_code in ('overdue', 'not_submitted', 'rejected')

	try:
		report_schedule.text_response = ReportScheduleTextResponse.objects.get(schedule=report_schedule)
	except ReportScheduleTextResponse.DoesNotExist:
		report_schedule.text_response = ''

	report_schedule.files = ReportScheduleFileResponse.objects.filter(schedule=report_schedule)

	return render_response(request, "page_report/report_overview.html", {'report_schedule':report_schedule, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL, })

