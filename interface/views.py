import calendar
from datetime import datetime, date
import os

from django.db.models import Q
from django.db.models import F

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
# FRONTPAGE
#
@login_required
def view_frontpage(request):
	if request.user.is_superuser:
		return _view_admin_frontpage(request)

	else:
		primary_role = request.user.groups.all()[0] # Currently support only 1 role per user

		if primary_role.name == "sector_admin":
			return _view_admin_frontpage(request)

		elif primary_role.name == "sector_manager":
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
	return redirect("/sector/%d/" % request.user.get_profile().sector.id)

def _view_sector_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile(), role__name="sector_manager_assistant")
	projects = responsibility.projects.all()
	for project in projects:
		project.reports = report_functions.get_submitted_and_overdue_reports(project)
		
	return render_response(request, "dashboard_assistant.html", {'projects':projects})

def _view_program_manager_frontpage(request):
<<<<<<< HEAD
	manager = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name='program_manager')
	program = manager[0].projects.all()[0]
	return redirect("/program/%d/" % program.id)
=======
	user_account = request.user.get_profile()
	return redirect("/sector/%d/" % user_account.sector.id)
>>>>>>> comment

def _view_program_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile(), role__name="program_manager_assistant")
	projects = responsibility.projects.all()
	for project in projects:
		project.reports = report_functions.get_all_reports_schedule_by_project(project)

	return render_response(request, "dashboard_program_assistant.html", {'projects':projects})

def _view_project_manager_frontpage(request):
<<<<<<< HEAD
	manager = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name='project_manager')
	project = manager[0].projects.all()[0]
	return redirect("/project/%d/" % project.id)	
=======
	user_account = request.user.get_profile()
	return redirect("/sector/%d/" % user_account.sector.id)
>>>>>>> comment

def _view_project_manager_assistant_frontpage(request):
	user_account = request.user.get_profile()
	return redirect("/sector/%d/" % user_account.sector.id)

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

@login_required
def view_administer_organization(request):
	user_account = request.user.get_profile()

	return render_response(request, "administer_organization.html", {})

@login_required
def view_administer_users(request):
	user_account = request.user.get_profile()

	return render_response(request, "administer_users.html", {})



#
# SECTOR
#
@login_required
def view_sector_overview(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today()
	current_year = current_date.year
	
	master_plans = MasterPlan.objects.filter(sector=sector, is_active=True, start_year__lte=current_year, end_year__gte=current_year)
	
	for master_plan in master_plans:
		master_plan.years = range(master_plan.start_year, master_plan.end_year+1)
		
		plans = Plan.objects.filter(master_plan=master_plan)

		for plan in plans:
			plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)
		
		master_plan.plans = plans
		
		# Finance KPI
		projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
		result = ProjectBudgetSchedule.objects.filter(project__in=projects, year=current_year).aggregate(Sum('expected_budget'), Sum('used_budget'))
		
		if result['expected_budget__sum']:
			master_plan.finance_kpi = int(float(result['used_budget__sum']) / float(result['expected_budget__sum']) * 100)
			if master_plan.finance_kpi > 100: master_plan.finance_kpi = 100
		else:
			master_plan.finance_kpi = None
		
		marked_projects = list()
		for result_project in ProjectBudgetSchedule.objects.filter(project__in=projects, scheduled_on__lt=current_date, claimed_on=None, year=current_year):
			marked_projects.append({'project':result_project.project, 'schedule':result_project})
			
		master_plan.finance_projects = marked_projects
		
		# Operation KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.OPERATION_CATEGORY)
		result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
		
		if result['target_score__sum']:
			master_plan.operation_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
			if master_plan.operation_kpi > 100: master_plan.operation_kpi = 100
		else:
			master_plan.operation_kpi = None
		
		marked_projects = list()
		for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
			percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
			if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
		
		master_plan.operation_projects = marked_projects
		
		# Teamwork KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.TEAMWORK_CATEGORY)
		result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
		
		if result['target_score__sum']:
			master_plan.teamwork_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
			if master_plan.teamwork_kpi > 100: master_plan.teamwork_kpi = 100
		else:
			master_plan.teamwork_kpi = None
		
		marked_projects = list()
		for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
			percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
			if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
		
		master_plan.teamwork_projects = marked_projects
		
		# Partner KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.PARTNER_CATEGORY)
		result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
		
		if result['target_score__sum']:
			master_plan.partner_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
			if master_plan.partner_kpi > 100: master_plan.partner_kpi = 100
		else:
			master_plan.partner_kpi = None
		
		marked_projects = list()
		for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
			percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
			if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
		
		master_plan.partner_projects = marked_projects
		
	return render_response(request, "sector_overview.html", {'sector':sector, 'master_plans':master_plans,})

@login_required
def view_sector_kpi(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today()
	
	master_plans = MasterPlan.objects.filter(sector=sector, is_active=True)
	
	for master_plan in master_plans:
		master_plan.years = range(master_plan.start_year, master_plan.end_year+1)
		
		# Finance KPI
		projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
		master_plan.finance_kpi = _get_sector_finance_kpi_percentage(master_plan)
		
		# Operation KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.OPERATION_CATEGORY)
		master_plan.operation_kpi = _get_sector_kpi_percentage(master_plan, kpis)
		
		# Teamwork KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.TEAMWORK_CATEGORY)
		master_plan.teamwork_kpi = _get_sector_kpi_percentage(master_plan, kpis)
		
		# Partner KPI
		kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.PARTNER_CATEGORY)
		master_plan.partner_kpi = _get_sector_kpi_percentage(master_plan, kpis)
		
	return render_response(request, "sector_kpi.html", {'sector':sector, 'master_plans':master_plans})

def _get_sector_finance_kpi_percentage(master_plan):
	current_date = date.today()
	
	projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
	
	if not projects: return None
	
	years_kpi = list()
	for year in master_plan.years:
		result = ProjectBudgetSchedule.objects.filter(project__in=projects, year=year).aggregate(Sum('expected_budget'), Sum('used_budget'))
		
		if result['expected_budget__sum']:
			percentage = int(float(result['used_budget__sum']) / float(result['expected_budget__sum']) * 100)
		else:
			percentage = None
		
		marked_projects = list()
		for result_project in ProjectBudgetSchedule.objects.filter(project__in=projects, scheduled_on__lt=current_date, claimed_on=None, year=year):
			marked_projects.append({'project':result_project.project, 'schedule':result_project})
		
		years_kpi.append({'percentage':percentage, 'projects':marked_projects})
	
	result = ProjectBudgetSchedule.objects.filter(project__in=projects).aggregate(Sum('expected_budget'), Sum('used_budget'))
	percentage = int(float(result['used_budget__sum']) / float(result['expected_budget__sum']) * 100) if result['expected_budget__sum'] else 0
	
	return {'years_kpi':years_kpi, 'total_percentage':percentage}

def _get_sector_kpi_percentage(master_plan, kpis):
	for kpi in kpis:
		years_kpi = list()
		for year in master_plan.years:
			result = KPISchedule.objects.filter(kpi=kpi, year=year).aggregate(Sum('target_score'), Sum('result_score'))
			
			print result
			
			if result['target_score__sum']:
				percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
			else:
				percentage = None
			
			marked_projects = list()
			for result_project in KPISchedule.objects.filter(kpi=kpi, year=year).values('project').annotate(Sum('target_score'), Sum('result_score')):
				project_percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
				if project_percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':project_percentage})
			
			years_kpi.append({'percentage':percentage, 'projects':marked_projects})
		
		kpi.years_kpi = years_kpi
		
		result = KPISchedule.objects.filter(kpi=kpi).aggregate(Sum('target_score'), Sum('result_score'))
		kpi.total_percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
		
	return kpis

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
	current_year = current_date.year
	
	master_plan.years = range(master_plan.start_year, master_plan.end_year+1)
	
	# Finance KPI
	projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
	result = ProjectBudgetSchedule.objects.filter(project__in=projects, year=current_year).aggregate(Sum('expected_budget'), Sum('used_budget'))
	
	if result['expected_budget__sum']:
		master_plan.finance_kpi = int(float(result['used_budget__sum']) / float(result['expected_budget__sum']) * 100)
		if master_plan.finance_kpi > 100: master_plan.finance_kpi = 100
	else:
		master_plan.finance_kpi = None
	
	marked_projects = list()
	for result_project in ProjectBudgetSchedule.objects.filter(project__in=projects, scheduled_on__lt=current_date, claimed_on=None, year=current_year):
		marked_projects.append({'project':result_project.project, 'schedule':result_project})
		
	master_plan.finance_projects = marked_projects
	
	# Operation KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.OPERATION_CATEGORY)
	result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	
	if result['target_score__sum']:
		master_plan.operation_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
		if master_plan.operation_kpi > 100: master_plan.operation_kpi = 100
	else:
		master_plan.operation_kpi = None
	
	marked_projects = list()
	for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
		percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
		if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
	
	master_plan.operation_projects = marked_projects
	
	# Teamwork KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.TEAMWORK_CATEGORY)
	result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	
	if result['target_score__sum']:
		master_plan.teamwork_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
		if master_plan.teamwork_kpi > 100: master_plan.teamwork_kpi = 100
	else:
		master_plan.teamwork_kpi = None
	
	marked_projects = list()
	for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
		percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
		if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
	
	master_plan.teamwork_projects = marked_projects
	
	# Partner KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.PARTNER_CATEGORY)
	result = KPISchedule.objects.filter(kpi__in=kpis, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	
	if result['target_score__sum']:
		master_plan.partner_kpi = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100)
		if master_plan.partner_kpi > 100: master_plan.partner_kpi = 100
	else:
		master_plan.partner_kpi = None
	
	marked_projects = list()
	for result_project in KPISchedule.objects.filter(kpi__in=kpis, year=current_year).values('project').annotate(Sum('target_score'), Sum('result_score')):
		percentage = int(float(result_project['result_score__sum']) / float(result_project['target_score__sum']) * 100) if result_project['target_score__sum'] else 0
		if percentage < 100: marked_projects.append({'project':Project.objects.get(pk=result_project['project']), 'percentage':percentage})
	
	master_plan.partner_projects = marked_projects
	
	# Plans
	plans = Plan.objects.filter(master_plan=master_plan)
	for plan in plans:
		plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)
		
	master_plan.plans = plans
	
	return render_response(request, "master_plan_overview.html", {'master_plan':master_plan, })

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

	master_plan.years = range(master_plan.start_year, master_plan.end_year+1)
	
	# Finance KPI
	projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
	master_plan.finance_kpi = _get_sector_finance_kpi_percentage(master_plan)
	
	# Operation KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.OPERATION_CATEGORY)
	master_plan.operation_kpi = _get_sector_kpi_percentage(master_plan, kpis)
	
	# Teamwork KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.TEAMWORK_CATEGORY)
	master_plan.teamwork_kpi = _get_sector_kpi_percentage(master_plan, kpis)
	
	# Partner KPI
	kpis = MasterPlanKPI.objects.filter(master_plan=master_plan, category=MasterPlanKPI.PARTNER_CATEGORY)
	master_plan.partner_kpi = _get_sector_kpi_percentage(master_plan, kpis)

	return render_response(request, "master_plan_kpi.html", {'master_plan':master_plan, })

#
# PROGRAM
#
@login_required
def view_program_overview(request, program_id):
	program = get_object_or_404(Project, pk=program_id)
	current_date = date.today()
	current_year = current_date.year
	
	current_projects = Project.objects.filter(parent_project=program, start_date__lte=current_date, end_date__gte=current_date)
	
	report_projects = ReportProject.objects.filter(project=program)
	report_schedules = ReportSchedule.objects.filter(report_project__in=report_projects, is_submitted=True, last_activity=APPROVE_ACTIVITY).order_by('-due_date')[:5]
	
	kpi = dict()
	
	# Finance KPI
	kpi['finance'] = {'current':dict(), 'year':dict()}
	
	# Note: Check against next finance schedule
	# Not have schedule -> 0%
	# Have only claimed schedule -> 100%
	# Have un-claimed schedule -> 0%
	
	past_schedules = ProjectBudgetSchedule.objects.filter(project=program, scheduled_on__lt=current_date)
	
	if not past_schedules:
		kpi['finance']['current'] = {'percentage':None, 'schedules':None}
		
	else:
		percentage = -1
		schedules = list()
		for past_schedule in past_schedules:
			if not past_schedule.claimed_on:
				percentage = 0
				schedules.append(past_schedule)
		
		if percentage == -1: percentage = 100
		
		kpi['finance']['current'] = {'percentage':percentage, 'schedules':schedules}
	
	result = ProjectBudgetSchedule.objects.filter(project=program, year=current_year).aggregate(Sum('expected_budget'), Sum('used_budget'))
	percentage = int(float(result['used_budget__sum']) / float(result['expected_budget__sum']) * 100) if result['expected_budget__sum'] else 0
	
	print result
	
	kpi['finance']['year'] = {'percentage':percentage}
	
	# Operation KPI
	kpi['operation'] = {'current':dict(), 'year':dict()}
	kpis = MasterPlanKPI.objects.filter(master_plan=program.master_plan, category=MasterPlanKPI.OPERATION_CATEGORY)
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	marked_kpis = list()
	for kpi_schedule in KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date, result_score__lt=F('target_score')):
		marked_kpis.append(kpi_schedule)
	
	kpi['operation']['current'] = {'percentage':percentage, 'kpi':marked_kpis}
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	kpi['operation']['year'] = {'percentage':percentage}
	
	# Teamwork KPI
	kpi['teamwork'] = {'current':dict(), 'year':dict()}
	kpis = MasterPlanKPI.objects.filter(master_plan=program.master_plan, category=MasterPlanKPI.TEAMWORK_CATEGORY)
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	marked_kpis = list()
	for kpi_schedule in KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date, result_score__lt=F('target_score')):
		marked_kpis.append(kpi_schedule)
	
	kpi['teamwork']['current'] = {'percentage':percentage, 'kpi':marked_kpis}
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	kpi['teamwork']['year'] = {'percentage':percentage}
	
	# Partner KPI
	kpi['partner'] = {'current':dict(), 'year':dict()}
	kpis = MasterPlanKPI.objects.filter(master_plan=program.master_plan, category=MasterPlanKPI.PARTNER_CATEGORY)
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	marked_kpis = list()
	for kpi_schedule in KPISchedule.objects.filter(kpi__in=kpis, project=program, start_date__lte=current_date, end_date__gte=current_date, result_score__lt=F('target_score')):
		marked_kpis.append(kpi_schedule)
	
	kpi['partner']['current'] = {'percentage':percentage, 'kpi':marked_kpis}
	
	result = KPISchedule.objects.filter(kpi__in=kpis, project=program, year=current_year).aggregate(Sum('target_score'), Sum('result_score'))
	percentage = int(float(result['result_score__sum']) / float(result['target_score__sum']) * 100) if result['target_score__sum'] else 0
	
	kpi['partner']['year'] = {'percentage':percentage}
	
	return render_response(request, "project_overview.html", {'project':program, 'kpi':kpi, 'current_year':current_year, 'current_projects':current_projects, 'report_schedules':report_schedules})

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
	current_year = current_date.year
	
	# Operation KPI
	kpi_ids = KPISchedule.objects.filter(project=program, kpi__category=MasterPlanKPI.OPERATION_CATEGORY, year=current_year).values('kpi').distinct()
	operation_kpis = list()
	
	for kpi_id in kpi_ids:
		operation_kpi = MasterPlanKPI.objects.get(id=kpi_id['kpi'])
		operation_kpi.schedules = KPISchedule.objects.filter(kpi=operation_kpi, project=program, year=current_year).order_by('-end_date')
		
		for schedule in operation_kpi.schedules:
			schedule.revisions = KPIScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
		
		operation_kpis.append(operation_kpi)
	
	# Teamwork KPI
	kpi_ids = KPISchedule.objects.filter(project=program, kpi__category=MasterPlanKPI.TEAMWORK_CATEGORY, year=current_year).values('kpi').distinct()
	teamwork_kpis = list()
	
	for kpi_id in kpi_ids:
		teamwork_kpi = MasterPlanKPI.objects.get(id=kpi_id['kpi'])
		teamwork_kpi.schedules = KPISchedule.objects.filter(kpi=teamwork_kpi, project=program, year=current_year).order_by('-end_date')
		
		for schedule in teamwork_kpi.schedules:
			schedule.revisions = KPIScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
		
		teamwork_kpis.append(teamwork_kpi)
	
	# Partner KPI
	kpi_ids = KPISchedule.objects.filter(project=program, kpi__category=MasterPlanKPI.PARTNER_CATEGORY, year=current_year).values('kpi').distinct()
	partner_kpis = list()
	
	for kpi_id in kpi_ids:
		partner_kpi = MasterPlanKPI.objects.get(id=kpi_id['kpi'])
		partner_kpi.schedules = KPISchedule.objects.filter(kpi=partner_kpi, project=program, year=current_year).order_by('-end_date')
		
		for schedule in partner_kpi.schedules:
			schedule.revisions = KPIScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
		
		partner_kpis.append(partner_kpi)
	
	return render_response(request, "project_kpi.html", {'project':program, 'operation_kpis':operation_kpis, 'teamwork_kpis':teamwork_kpis, 'partner_kpis':partner_kpis})

@login_required
def view_program_finance(request, program_id):
	program = get_object_or_404(Project, pk=program_id)
	
	year_ids = ProjectBudgetSchedule.objects.filter(project=program).values('year').distinct()
	finance_years = list()
	
	for year_id in year_ids:
		schedules = ProjectBudgetSchedule.objects.filter(project=program, year=year_id['year']).order_by('-scheduled_on')
		
		for schedule in schedules:
			schedule.revisions = ProjectBudgetScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
		
		finance_years.append({'number':year_id['year'], 'schedules':schedules})
	
	return render_response(request, "project_finance.html", {'project':program, 'finance_years':finance_years})

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

	report_projects = ReportProject.objects.filter(project=project)
	report_schedules = ReportSchedule.objects.filter(report_project__in=report_projects, is_submitted=True, last_activity=APPROVE_ACTIVITY).order_by('-due_date')
	
	current_activities = project.activity_set.filter(start_date__lte=current_date, end_date__gte=current_date).order_by('end_date')
	future_activities = project.activity_set.filter(start_date__gt=current_date).order_by('start_date')
	return render_response(request, "project_overview.html", {'project':project, 'current_activities':current_activities, 'future_activities':future_activities, 'report_schedules':report_schedules})

# Helper function to find previous and next month.
def prev_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	month_index = MONTH.index(month)
	prev_index = month_index - num
	if abs(prev_index) > 12:
		prev_index = 12 % prev_index

	if prev_index < 0:
		year = year + (prev_index / 12)

	return (year, MONTH[prev_index])

def next_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	delta = num
	index = month + num

	return (year + (index / 13), MONTH[index % 12 - 1])

@login_required
def view_project_activities(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	current_date = date.today()
	current_activities = Activity.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)
	future_activities = Activity.objects.filter(project=project, start_date__gt=current_date)
	past_activities = Activity.objects.filter(project=project, end_date__lt=current_date)

	# Find activities in past month, current month and next month.
	num = 3
	prev_month_ = prev_month(current_date.year, current_date.month, num)
	start = date(*prev_month_, day=1)
	next_month_ = next_month(current_date.year, current_date.month, num)
	end = date(*next_month_, day=calendar.monthrange(*next_month_)[1])

	prev_month_ = "%04d%02d" % prev_month(current_date.year, current_date.month)
	next_month_ = "%04d%02d" % next_month(current_date.year, current_date.month)

	recent_activities = Activity.objects.filter(project=project).filter( \
		Q(start_date__lte=start) & Q(end_date__gte=end) | \
		Q(start_date__lte=end) & Q(start_date__gte=start) | \
		Q(end_date__lte=end) & Q(end_date__gte=start))

	return render_response(request, "project_activities.html", {'project':project, 'current_activities':current_activities, 'future_activities':future_activities, 'past_activities':past_activities,'recent_activities':recent_activities,'prev_month':prev_month_,'next_month':next_month_})

@login_required
def view_project_activities_ajax(request, project_id, yearmonth):
	project = get_object_or_404(Project, pk=project_id)

	year = int(yearmonth[:4])
	month = int(yearmonth[4:])

	# Find activities in past month, current month and future month.
	num = 3
	prev_month_ = prev_month(year, month, num)
	next_month_ = next_month(year, month, num)

	start = date(*prev_month_, day=1)
	end = date(*next_month_, day=calendar.monthrange(*next_month_)[1])

	prev_month_ = "%04d%02d" % prev_month(year, month)
	next_month_ = "%04d%02d" % next_month(year, month)

	recent_activities = Activity.objects.filter(project=project).filter( \
		Q(start_date__lte=start) & Q(end_date__gte=end) | \
		Q(start_date__lte=end) & Q(start_date__gte=start) | \
		Q(end_date__lte=end) & Q(end_date__gte=start))

	return render_response(request, "project_activities_ajax.html", {'recent_activities':recent_activities,'prev_month':prev_month_,'next_month':next_month_})

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
