import calendar
from django.db.models import Q
from datetime import datetime, date
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from thaihealthsms.shortcuts import render_response

from comments.models import *
from domain.models import *
from report.models import *

from interface.forms import *

from domain import functions as domain_functions
from report import functions as report_functions
from helper.utilities import set_message

def view_frontpage(request):
	if request.user.is_authenticated(): return view_dashboard(request)
	else: return redirect("/accounts/login/")

#
# DASHBOARD
#
@login_required
def view_dashboard(request):
	if request.user.is_superuser:
		return _view_admin_frontpage(request)
	
	else:
		primary_role = request.user.groups.all()[0]
		
		if primary_role.name == "sector_manager":
			return _view_sector_manager_frontpage(request)
			
		elif primary_role.name == "sector_manager_assistant":
			return _view_sector_manager_assistant_frontpage(request)
			
		elif primary_role.name == "program_manager":
			return _view_program_manager_frontpage(request)
			
		elif primary_role.name == "program_manager_assistant":
			return _view_program_manager_assistant_frontpage(request)
			
		elif primary_role.name == "project_manager":
			return _view_project_manager_frontpage(request)
			
		elif primary_role.name == "project_manager_assistant":
			return _view_project_manager_assistant_frontpage(request)

def _view_admin_frontpage(request):
	return redirect("/administer/")

def _view_sector_manager_frontpage(request):
	return redirect("/sector/%d/" % user_account.sector.id)

def _view_sector_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile(), role__name="sector_manager_assistant")
	
	return render_response(request, "dashboard_assistant.html", {'projects':responsibility.projects.all()})

def _view_program_manager_frontpage(request):
	return redirect("/sector/%d/" % user_account.sector.id)

def _view_program_manager_assistant_frontpage(request):
	return redirect("/sector/%d/" % user_account.sector.id)

def _view_project_manager_frontpage(request):
	return redirect("/sector/%d/" % user_account.sector.id)

def _view_project_manager_assistant_frontpage(request):
	return redirect("/sector/%d/" % user_account.sector.id)




def _view_assistant_frontpage(request, user_account):
	user_projects = user_account.projects.all()
	for user_project in user_projects:
		user_project.reports = report_functions.get_submitted_and_overdue_reports(user_project)

	return render_response(request, "dashboard_assistant.html", {'user_projects':user_projects})


@login_required
def view_dashboard_projects(request):
	user_account = request.user.get_profile()

	if user_account.role == "assistant":
		user_projects = user_account.projects.all()

		programs = list()
		projects = list()

		for user_project in user_projects:
			if user_project.type == Project.PROGRAM_TYPE: programs.append(user_project)
			if user_project.type == Project.PROJECT_TYPE: projects.append(user_project)

		return render_response(request, "dashboard_assistant_projects.html", {'programs':programs,'projects':projects})

	else:
		pass

@login_required
def view_dashboard_comments(request):
	user_account = request.user.get_profile()
	
	comments = CommentReceiver.objects.filter(receiver=request.user.get_profile(), is_read=False).order_by("-sent_on")
	
	object_list = list()
	object_dict = dict()

	for comment in comments:
		hash_str = "%s%d" % (comment.comment.object_name, comment.comment.object_id)
		if hash_str not in object_list:
			object = None

			if comment.comment.object_name == "activity":
				object = Activity.objects.get(pk=comment.comment.object_id)

			elif comment.comment.object_name == "project" or comment.comment.object_name == "program":
				object = Project.objects.get(pk=comment.comment.object_id)

			elif comment.comment.object_name == "report":
				object = ReportSchedule.objects.get(pk=comment.comment.object_id)

			if object:
				object_list.append(hash_str)
				object_dict[hash_str] = {'comment':comment.comment, 'object':object, 'comments':[comment]}

		else:
			object_dict[hash_str]['comments'].append(comment)

	objects = list()
	for object_hash in object_list:
		objects.append(object_dict[object_hash])

	return render_response(request, "dashboard_comments.html", {'objects':objects})

#
# ADMIN
#
@login_required
def view_administer(request):
	user_account = request.user.get_profile()

	return render_response(request, "administer.html", {})


#
# SECTOR
#
@login_required
def view_sector_overview(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today()
	
	master_plans = MasterPlan.objects.filter(sector=sector, is_active=True)
	
	for master_plan in master_plans:
		finance_result = FinanceKPISubmission.objects.filter(project__master_plan=master_plan, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("budget"), Sum("spent_budget"))
		master_plan.finance_percentage = int(float(finance_result["spent_budget__sum"] if finance_result["spent_budget__sum"] else "0") / float(finance_result["budget__sum"] if finance_result["budget__sum"] else "100") * 100)
		
		operation_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.OPERATION_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
		master_plan.operation_percentage = int(float(operation_result["result_score__sum"] if operation_result["result_score__sum"] else "0") / float(operation_result["target_score__sum"] if operation_result["target_score__sum"] else "100") * 100)
		
		teamwork_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.TEAMWORK_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
		master_plan.teamwork_percentage = int(float(teamwork_result["result_score__sum"] if teamwork_result["result_score__sum"] else "0") / float(teamwork_result["target_score__sum"] if teamwork_result["target_score__sum"] else "100") * 100)
		
		partner_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.PARTNER_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
		master_plan.partner_percentage = int(float(partner_result["result_score__sum"] if partner_result["result_score__sum"] else "0") / float(partner_result["target_score__sum"] if partner_result["target_score__sum"] else "100") * 100)
	
	return render_response(request, "sector_overview.html", {'sector':sector, 'master_plans':master_plans,})

@login_required
def view_sector_master_plans(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today()

	master_plans = MasterPlan.objects.filter(sector=sector, is_active=True)

	for master_plan in master_plans:
		master_plan.plans = Plan.objects.filter(master_plan=master_plan)

		for plan in master_plan.plans:
			plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)
			plan.future_projects = Project.objects.filter(plan=plan, start_date__gt=current_date)
			plan.past_projects = Project.objects.filter(plan=plan, end_date__lt=current_date)

		master_plan.projects = Project.objects.filter(master_plan=master_plan, plan=None, parent_project=None)

	return render_response(request, "sector_master_plans.html", {'sector':sector, 'master_plans':master_plans})

@login_required
def view_sectors_overview(request):
	sectors = Sector.objects.all()

	for sector in sectors:
		sector.master_plans = MasterPlan.objects.filter(sector=sector, is_active=True)

	return render_response(request, "sectors_overview.html", {'sectors':sectors})

#
# MASTER PLAN
#
@login_required
def view_master_plan_overview(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	
	current_date = date.today()
	
	#finance_result = FinanceKPISubmission.objects.filter(project__master_plan=master_plan, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("budget"), Sum("spent_budget"))
	#finance_percentage = int(float(finance_result["spent_budget__sum"]) / float(finance_result["budget__sum"]) * 100)
	
	#operation_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.OPERATION_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
	#operation_percentage = int(float(operation_result["result_score__sum"]) / float(operation_result["target_score__sum"]) * 100)
	
	#teamwork_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.TEAMWORK_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
	#teamwork_percentage = int(float(teamwork_result["result_score__sum"]) / float(teamwork_result["target_score__sum"]) * 100)
	
	#partner_result = KPISubmission.objects.filter(target__kpi__master_plan=master_plan, target__kpi__category=MasterPlanKPI.PARTNER_CATEGORY, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
	#partner_percentage = int(float(partner_result["result_score__sum"]) / float(partner_result["target_score__sum"]) * 100)
	
	finance_percentage = 50
	operation_percentage = 50
	teamwork_percentage = 50
	partner_percentage = 50
	
	return render_response(request, "master_plan_overview.html", {'master_plan':master_plan, 'finance_percentage':finance_percentage, 'operation_percentage':operation_percentage, 'teamwork_percentage':teamwork_percentage, 'partner_percentage':partner_percentage})

@login_required
def view_master_plan_plans(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	current_date = date.today()
	
	plans = Plan.objects.filter(master_plan=master_plan)
	
	for plan in plans:
		plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)
		plan.future_projects = Project.objects.filter(plan=plan, start_date__gt=current_date)
		plan.past_projects = Project.objects.filter(plan=plan, end_date__lt=current_date)
		
	return render_response(request, "master_plan_plans.html", {'master_plan':master_plan, 'plans':plans})

@login_required
def view_master_plan_kpi(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	current_date = date.today()
	
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan)
	
	for kpi in kpis:
		kpi.target_projects = KPITargetProject.objects.filter(kpi=kpi)
		
		for target_project in kpi.target_projects:
			result = KPISubmission.objects.filter(target=target_project, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("target_score"), Sum("result_score"))
			
			target_project.target_score = result["target_score__sum"]
			target_project.result_score = result["result_score__sum"]
			
			target_project.percentage = int((float(target_project.result_score) / float(target_project.target_score)) * 100)
			
			if target_project.percentage < 50: target_project.range = "lowest"
			elif target_project.percentage < 100: target_project.range = "low"
			elif target_project.percentage == 100: target_project.range = "expect"
			else: target_project.range = "above"
	
	# Finance KPI
	projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
	
	for project in projects:
		result = FinanceKPISubmission.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum("budget"), Sum("spent_budget"))
		
		project.budget = result["budget__sum"]
		if not project.budget: project.budget = "100"
		project.spent_budget = result["spent_budget__sum"]
		if not project.spent_budget: project.spent_budget = "0"
		
		project.percentage = int((float(project.spent_budget) / float(project.budget)) * 100)
		
		if project.percentage < 50: project.range = "lowest"
		elif project.percentage < 100: project.range = "low"
		elif project.percentage == 100: project.range = "expect"
		else: project.range = "above"
	
	return render_response(request, "master_plan_kpi.html", {'master_plan':master_plan, 'kpis':kpis, 'projects':projects})

#
# PROGRAM
#
@login_required
def view_program_overview(request, program_id):
	program = get_object_or_404(Project, pk=program_id)
	return render_response(request, "project_overview.html", {'project':program})

@login_required
def view_program_projects(request, program_id):
	program = get_object_or_404(Project, pk=program_id)

	current_date = date.today()
	current_projects = Project.objects.filter(parent_project=program, start_date__lte=current_date, end_date__gte=current_date)
	future_projects = Project.objects.filter(parent_project=program, start_date__gt=current_date)
	past_projects = Project.objects.filter(parent_project=program, end_date__lt=current_date)

	return render_response(request, "project_projects.html", {'project':program, 'current_projects':current_projects, 'future_projects':future_projects, 'past_projects':past_projects})

@login_required
def view_program_reports(request, program_id):
	program = get_object_or_404(Project, pk=program_id)

	report_projects = ReportProject.objects.filter(project=program)

	report_schedules = ReportSchedule.objects.filter(report_project__in=report_projects, is_submitted=True).order_by('-due_date')

	year_list = set()
	for report_schedule in report_schedules: year_list.add(report_schedule.due_date.year)

	year_list = sorted(year_list, reverse=True)

	return render_response(request, "project_reports.html", {'project':program, 'report_schedules':report_schedules, 'year_list':year_list})

@login_required
def view_program_reports_send(request, program_id):
	program = get_object_or_404(Project, pk=program_id)
	reports = report_functions.get_nextdue_and_overdue_reports(program_id)

	for report in reports:
		for schedule in report.schedules:
			schedule.files = ReportScheduleFileResponse.objects.filter(schedule=schedule)

	if request.method == "POST":
		if request.POST.get("submit") == "schedule_upload":
			schedule_id = request.POST.get("schedule_id")
			due_date = request.POST.get("due_date")

			schedule = ReportSchedule.objects.get(pk=schedule_id)

			# Store uploading file
			uploading_file = request.FILES['uploading_file']
			uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, schedule.report_project.report.id, schedule.id)

			if not os.path.exists(uploading_directory): os.makedirs(uploading_directory)

			ReportScheduleFileResponse.objects.create(schedule=schedule, filename=uploading_file.name, uploaded_by=request.user.get_profile())

			destination = open(uploading_directory + uploading_file.name, 'wb')
			for chunk in request.FILES['uploading_file'].chunks(): destination.write(chunk)
			destination.close()

		elif request.POST.get("submit") == "schedule_submit":
			schedule_id = request.POST.get("schedule_id")
			due_date = request.POST.get("due_date")

			schedule = ReportSchedule.objects.get(pk=schedule_id)
			schedule.is_submitted = True
			schedule.submitted = datetime.now()
			schedule.save()


		return redirect("/program/%d/reports/send/" % program.id)


	return render_response(request, "project_reports_send.html", {'project':program, 'reports':reports, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL})

@login_required
def view_program_kpi(request, program_id):
	program = get_object_or_404(Project, pk=program_id)
	current_date = date.today()
	
	kpi_targets = KPITargetProject.objects.filter(project=program)
	
	for kpi_target in kpi_targets:
		kpi_target.current_submission = KPISubmission.objects.filter(target=kpi_target, start_date__lte=current_date, end_date__gte=current_date).order_by("-end_date")
		for submission_item in kpi_target.current_submission: submission_item.revisions = KPISubmissionRevision.objects.filter(submission=submission_item).order_by("-submitted_on")
		
		kpi_target.last_submission = KPISubmission.objects.filter(target=kpi_target, end_date__lt=current_date).order_by("-end_date")
		for submission_item in kpi_target.last_submission: submission_item.revisions = KPISubmissionRevision.objects.filter(submission=submission_item).order_by("-submitted_on")
	
	current_finance_submission = FinanceKPISubmission.objects.filter(project=program, start_date__lte=current_date, end_date__gte=current_date).order_by("-end_date")
	for submission_item in current_finance_submission: submission_item.revisions = FinanceKPISubmissionRevision.objects.filter(submission=submission_item).order_by("-submitted_on")
	
	last_finance_submission = FinanceKPISubmission.objects.filter(project=program, end_date__lt=current_date).order_by("-end_date")
	for submission_item in last_finance_submission: submission_item.revisions = FinanceKPISubmissionRevision.objects.filter(submission=submission_item).order_by("-submitted_on")
	
	return render_response(request, "project_kpi.html", {'project':program, 'kpi_targets':kpi_targets, 'current_finance_submission':current_finance_submission, 'last_finance_submission':last_finance_submission})

@login_required
def view_program_comments(request, program_id):
	program = get_object_or_404(Project, pk=program_id)

	comments = CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='program', comment__object_id=program_id).order_by("-sent_on")

	for comment in comments:
		comment.receivers = CommentReceiver.objects.filter(comment=comment.comment)
		comment.already_read = comment.is_read

	CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='program', comment__object_id=program_id).update(is_read=True)

	return render_response(request, "project_comments.html", {'project':program, 'comments':comments})

#
# PROJECT
#
@login_required
def view_project_overview(request, project_id):
	current_date = date.today()
	project = get_object_or_404(Project, pk=project_id)
	current_activities = project.activity_set.filter(start_date__lte=current_date, end_date__gte=current_date).order_by('end_date')
	future_activities = project.activity_set.filter(start_date__gt=current_date).order_by('start_date')
	return render_response(request, "project_overview.html", {'project':project, 'current_activities':current_activities, 'future_activities':future_activities})

@login_required
def view_project_activities(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	current_date = date.today()
	current_activities = Activity.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)
	future_activities = Activity.objects.filter(project=project, start_date__gt=current_date)
	past_activities = Activity.objects.filter(project=project, end_date__lt=current_date)
	all_activities = Activity.objects.filter(project=project)

	return render_response(request, "project_activities.html", {'project':project, 'current_activities':current_activities, 'future_activities':future_activities, 'past_activities':past_activities,'all_activities':all_activities})

@login_required
def view_project_reports(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	return render_response(request, "project_reports.html", {'project':project})

@login_required
def view_project_reports_send(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	reports = report_functions.get_nextdue_and_overdue_reports(project_id)

	for report in reports:
		for schedule in report.schedules:
			schedule.files = ReportScheduleFileResponse.objects.filter(schedule=schedule)

	return render_response(request, "project_reports_send.html", {'project':project, 'reports':reports, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL})

@login_required
def view_activity_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	message = ''
	if request.method == "POST":
		form = AddActivityForm(request.POST)
		if form.is_valid():
			activity = Activity()

			activity.project     = project
			activity.name        = form.cleaned_data['name']
			activity.start_date  = form.cleaned_data['start_date']
			activity.end_date    = form.cleaned_data['end_date']
			activity.description = form.cleaned_data['description']
			activity.location    = form.cleaned_data['location']
			activity.result_goal = form.cleaned_data['result_goal']
			activity.result_real = form.cleaned_data['result_real']
			activity.save()

			set_message(request, 'Your activity has been create.')
			
			return redirect("/activity/%d/" % activity.id)

	else:
		form = AddActivityForm()

	return render_response(request, "project_activity_add.html", {'project':project, 'form':form, 'message': message})

@login_required
def view_activity_edit(request, activity_id):
	activity = Activity.objects.get(pk=activity_id)
	project = activity.project
	
	if request.method == "POST":
		form = AddActivityForm(request.POST)
		if form.is_valid():
			activity.name        = form.cleaned_data['name']
			activity.start_date  = form.cleaned_data['start_date']
			activity.end_date    = form.cleaned_data['end_date']
			activity.description = form.cleaned_data['description']
			activity.location    = form.cleaned_data['location']
			activity.result_goal = form.cleaned_data['result_goal']
			activity.result_real = form.cleaned_data['result_real']
			activity.save()
			
			set_message(request, 'Your activity has been update.')

			return redirect("/activity/%d/" % activity.id)
			
	form = AddActivityForm(activity.__dict__)
	return render_response(request, "project_activity_edit.html", {'project':project, 'form':form})

@login_required
def view_activity_delete(request, activity_id):
	activity = Activity.objects.get(pk=activity_id)
	project = activity.project
	activity.delete()
	
	set_message(request, 'Your activity has been delete.')
	
	return redirect("/project/%d/activities/" % project.id)
	
@login_required
def view_project_comments(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	comments = Comment.objects.filter(object_name="project", object_id=project_id).order_by("-sent_on")

	return render_response(request, "project_comments.html", {'project':project, 'comments':comments})

#
# ACTIVITY
#

@login_required
def view_activity_overview(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)
	return render_response(request, "activity_overview.html", {'activity':activity,})

@login_required
def view_activity_pictures(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)

	return render_response(request, "activity_pictures.html", {'activity':activity, })

@login_required
def view_activity_comments(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)

	comments = Comment.objects.filter(object_name="activity", object_id=activity_id).order_by("-sent_on")

	return render_response(request, "activity_comments.html", {'activity':activity, 'comments':comments, })

#
# REPORT
#

@login_required
def view_report_overview(request, report_id):
	report_schedule = get_object_or_404(ReportSchedule, pk=report_id)
	report_schedule.files = ReportScheduleFileResponse.objects.filter(schedule=report_schedule)
	return render_response(request, "report_overview.html", {'report_schedule':report_schedule, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL, })

@login_required
def view_report_comments(request, report_id):
	report_schedule = get_object_or_404(ReportSchedule, pk=report_id)

	comments = Comment.objects.filter(object_name="report", object_id=report_id).order_by("-sent_on")

	return render_response(request, "report_comments.html", {'report_schedule':report_schedule, 'comments':comments, })

