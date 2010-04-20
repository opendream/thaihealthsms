# -*- encoding: utf-8 -*-
import calendar
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from accounts.models import *
from finance.models import *
from kpi.models import *
from report.models import *

from finance import functions as finance_functions
from report import functions as report_functions

from helper import utilities
from helper.message import set_message
from helper.shortcuts import render_response, access_denied

#
# SECTOR #######################################################################
#
@login_required
def view_sectors(request):
	sectors = Sector.objects.all().order_by('ref_no')
	
	for sector in sectors:
		sector.master_plans = MasterPlan.objects.filter(sector=sector).order_by('ref_no')

	return render_response(request, 'page_sector/sectors_overview.html', {'sectors':sectors})

@login_required
def view_sector_overview(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	
	master_plans = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
	
	from kpi.functions import get_kpi_summary_by_category
	
	for master_plan in master_plans:
		# KPI #
		kpi_categories = list()
		
		master_plan.current_year = utilities.master_plan_current_year_number(master_plan) + 543
		master_plan.previous_year = master_plan.current_year - 1
		
		for category in KPISchedule.objects.filter(kpi__master_plan=None, project__master_plan=master_plan).values('kpi__category').distinct():
			kpi_category = KPICategory.objects.get(pk=category['kpi__category'])
			kpi_categories.append(get_kpi_summary_by_category(kpi_category, master_plan, True))
		
		for category in KPI.objects.filter(master_plan=master_plan).values('category').distinct():
			kpi_category = KPICategory.objects.get(pk=category['category'])
			kpi_categories.append(get_kpi_summary_by_category(kpi_category, master_plan, False))
		
		master_plan.categories = kpi_categories
		
		# Finance #
		master_plan = finance_functions.overview_master_plan_finance(master_plan)
	
	return render_response(request, 'page_sector/sector_overview.html', {'sector':sector, 'master_plans':master_plans,})

@login_required
def view_sector_manage_organization(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today().replace(day=1)
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	master_plans = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
	
	for master_plan in master_plans:
		plans = Plan.objects.filter(master_plan=master_plan)
		
		for plan in plans:
			plan.projects = Project.objects.filter(plan=plan).order_by('ref_no')
			for project in plan.projects:
				if Project.objects.filter(parent_project=project).count() or ReportSchedule.objects.filter(report_project__project=project).exclude(state=NO_ACTIVITY).count():
					project.has_child = True
		
		master_plan.plans = plans
	
	return render_response(request, 'page_sector/sector_manage_organization.html', {'sector':sector, 'master_plans':master_plans})

# MANAGE ORGANIZATION - PLAN

@login_required
def view_sector_add_plan(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyPlanForm(request.POST, sector=sector)
		if form.is_valid():
			plan = Plan.objects.create(ref_no=form.cleaned_data['ref_no'], name=form.cleaned_data['name'], master_plan=form.cleaned_data['master_plan'])
			
			set_message(request, u'สร้างกลุ่มแผนงานเรียบร้อย')
			return redirect('view_sector_manage_organization', (sector.id))
	else:
		form = ModifyPlanForm(sector=sector)
	
	return render_response(request, 'page_sector/sector_manage_modify_plan.html', {'sector':sector, 'form':form})

@login_required
def view_sector_edit_plan(request, plan_id):
	plan = get_object_or_404(Plan, pk=plan_id)
	sector = plan.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyPlanForm(request.POST, sector=sector)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			plan.master_plan = cleaned_data['master_plan']
			plan.ref_no = cleaned_data['ref_no']
			plan.name = cleaned_data['name']
			plan.save()
			
			set_message(request, u'แก้ไขกลุ่มแผนงานเรียบร้อย')
			return redirect('view_sector_manage_organization', (sector.id))
	else:
		form = ModifyPlanForm(sector=sector, initial={'plan_id':plan.id, 'master_plan':plan.master_plan.id, 'ref_no':plan.ref_no, 'name':plan.name})
	
	return render_response(request, 'page_sector/sector_manage_modify_plan.html', {'sector':sector, 'plan':plan, 'form':form})

@login_required
def view_sector_delete_plan(request, plan_id):
	plan = get_object_or_404(Plan, pk=plan_id)
	sector = plan.master_plan.sector

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)

	if not Project.objects.filter(plan=plan).count():
		plan.delete()
		set_message(request, u'ลบกลุ่มแผนงานเรียบร้อย')
	else:
		set_message(request, u'ไม่สามารถลบกลุ่มแผนงานได้ เนื่องจากมีแผนงานที่อยู่ภายใต้')
	
	return redirect('view_sector_manage_organization', (sector.id))

# MANAGE ORGANIZATION - PROJECT

@login_required
def view_sector_add_project(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if request.method == 'POST':
		form = MasterPlanProjectForm(request.POST, sector=sector)
		if form.is_valid():
			project = Project.objects.create(
				master_plan=form.cleaned_data['plan'].master_plan,
				plan=form.cleaned_data['plan'],
				prefix_name=Project.PROJECT_IS_PROGRAM,
				ref_no=form.cleaned_data['ref_no'],
				name=form.cleaned_data['name'],
				start_date=form.cleaned_data['start_date'],
				end_date=form.cleaned_data['end_date'],
				)
			
			set_message(request, u'สร้างแผนงานเรียบร้อย คุณสามารถเพิ่มรายงาน ตัวชี้วัด และแผนการเงิน ได้จากหน้าแก้ไขแผนงานนี้')
			return redirect('view_sector_edit_project', (project.id))
		
	else:
		form = MasterPlanProjectForm(sector=sector)
	
	has_plans = Plan.objects.filter(master_plan__sector=sector).count() > 0
	return render_response(request, 'page_sector/sector_manage_add_project.html', {'sector':sector, 'form':form, 'has_plans':has_plans})

@login_required
def view_sector_edit_project(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	sector = project.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	project = get_object_or_404(Project, pk=project_id)
	
	if request.method == 'POST':
		form = MasterPlanProjectForm(request.POST, sector=sector)
		if form.is_valid():
			project.plan = form.cleaned_data['plan']
			project.ref_no = form.cleaned_data['ref_no']
			project.name = form.cleaned_data['name']
			project.start_date = form.cleaned_data['start_date']
			project.end_date = form.cleaned_data['end_date']
			project.save()
			
			set_message(request, u'แก้ไขแผนงานเรียบร้อย')
			return redirect('view_sector_edit_project', (project.id))
		
	else:
		form = MasterPlanProjectForm(sector=sector, initial={'project_id':project.id, 'plan':project.plan.id, 'ref_no':project.ref_no, 'name':project.name, 'description':project.description, 'start_date':project.start_date, 'end_date':project.end_date})
	
	return render_response(request, 'page_sector/sector_manage_edit_project.html', {'sector':sector, 'project':project, 'form':form})

@login_required
def view_sector_delete_project(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	sector = project.master_plan.sector

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if Project.objects.filter(parent_project=project).count() or ReportSchedule.objects.filter(report_project__project=project).exclude(state=NO_ACTIVITY).count():
		set_message(request, u'ไม่สามารถลบแผนงานได้ เนื่องจากแผนงานยังมีโครงการหรือรายงานอยู่')

	else:
		ReportSchedule.objects.filter(report_project__project=project, state=NO_ACTIVITY).delete()
		ReportProject.objects.filter(project=project).delete()
		project.delete()
		set_message(request, u'ลบแผนงานเรียบร้อย')

	return redirect('view_sector_manage_organization', (sector.id))

#
# MASTER PLAN #######################################################################
#
@login_required
def view_master_plan_overview(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	current_date = date.today()

	# Plans
	plans = Plan.objects.filter(master_plan=master_plan)
	for plan in plans:
		plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)

	master_plan.plans = plans
	master_plan = finance_functions.overview_master_plan_finance(master_plan)
	return render_response(request, 'page_master_plan/master_plan_overview.html', {'master_plan': master_plan})

@login_required
def view_master_plan_report(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	year_span = utilities.master_plan_current_year_span(master_plan)
	current_date = date.today()

	# Plans
	plans = Plan.objects.filter(master_plan=master_plan)
	for plan in plans:
		plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)
		for project in plan.current_projects:
			budgets = ProjectBudgetSchedule.objects.filter(project=project.id, target_on__range=year_span)
			sum_budget = 0
			for b in budgets:
				sum_budget += b.target
			project.budget = sum_budget

			quarters = []
			start_month = year_span[0].month
			start_year = year_span[0].year
			for i in range(4):
				end_month = start_month + 2
				end_year = start_year
				if end_month > 12:
					end_month = end_month - 12
					end_year = start_year + 1
				
				start = date(start_year, start_month, 1)
				end = date(end_year, end_month, calendar.monthrange(end_year, end_month)[1])

				kpis = KPISchedule.objects.filter(project=project, target_on__range=(start, end)).values('kpi').distinct()
				kpi_list = []
				for kpi in kpis:
					kpi_object = KPI.objects.get(id=kpi['kpi'])
					sum_target = KPISchedule.objects.filter(project=project, target_on__range=(start, end), \
															kpi=kpi_object) \
									.aggregate(Sum('target'))['target__sum']
					sum_result = KPISchedule.objects.filter(project=project, target_on__range=(start, end), \
															kpi=kpi_object) \
									.aggregate(Sum('result'))['result__sum']
					kpi_list.append({'kpi': kpi_object, 'sum_target': sum_target, 'sum_result': sum_result})

				start_month = start_month + 3
				if start_month > 12:
					start_month = start_month - 12
					start_year = start_year + 1

				quarters.append({'start': start, 'end': end, 'kpi_list': kpi_list})
			project.quarters = quarters

	master_plan.plans = plans
	master_plan = finance_functions.overview_master_plan_finance(master_plan)
	return render_response(request, 'page_master_plan/master_plan_report.html', {'master_plan': master_plan})

@login_required
def view_master_plan_plans(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	plans = Plan.objects.filter(master_plan=master_plan)

	for plan in plans:
		plan.projects = Project.objects.filter(plan=plan).order_by('-start_date')

	return render_response(request, 'page_master_plan/master_plan_plans.html', {'master_plan':master_plan, 'plans':plans})

@login_required
def view_master_plan_organization(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', master_plan.sector):
		return access_denied(request)

	plans = Plan.objects.filter(master_plan=master_plan)

	for plan in plans:
		plan.projects = Project.objects.filter(plan=plan).order_by('-start_date')
		for project in plan.projects:
			if Project.objects.filter(parent_project=project).count() or ReportSchedule.objects.filter(report_project__project=project).exclude(state=NO_ACTIVITY).count():
				project.has_child = True

	return render_response(request, 'page_master_plan/master_plan_organization.html', {'master_plan':master_plan, 'plans':plans})

#
# PROJECT #######################################################################
#
@login_required
def view_project_overview(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	current_date = date.today()

	if not project.parent_project:
		current_projects = Project.objects.filter(parent_project=project, start_date__lte=current_date, end_date__gte=current_date)
		report_schedules = ReportSchedule.objects.filter(report_project__project=project).filter(Q(state=APPROVE_ACTIVITY) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_approval=False)) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_checkup=False))).order_by('-schedule_date')[:5]
		finances = finance_functions.overview_project_finance(project)
		return render_response(request, 'page_project/project_overview.html', {'project':project, 'current_projects':current_projects, 'report_schedules':report_schedules, 'finances':finances})

	else:
		current_activities = Activity.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)
		return render_response(request, 'page_project/project_overview.html', {'project':project, 'current_activities':current_activities})

@login_required
def view_project_projects(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	projects = Project.objects.filter(parent_project=project).order_by('-start_date')

	return render_response(request, 'page_project/project_projects.html', {'project':project, 'projects':projects})

@login_required
def view_project_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		if request.method == 'POST':
			form = ModifyProjectForm(request.POST)
			if form.is_valid():
				created_project = Project.objects.create(
					master_plan=project.master_plan,
					parent_project=project,
					prefix_name=Project.PROJECT_IS_PROJECT,
					ref_no=form.cleaned_data['ref_no'],
					name=form.cleaned_data['name'],
					start_date=form.cleaned_data['start_date'],
					end_date=form.cleaned_data['end_date']
				)

				set_message(request, u'สร้างโครงการเรียบร้อย')
				return redirect('view_project_overview', (created_project.id))

		else:
			form = ModifyProjectForm(initial={'parent_project_id':project.id})

		return render_response(request, 'page_project/project_projects_add.html', {'project':project, 'form':form})

	else:
		return redirect('view_project_projects', (project.id))

@login_required
def view_project_edit(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project.parent_project):
		if request.method == 'POST':
			form = ModifyProjectForm(request.POST)
			if form.is_valid():
				project.ref_no = form.cleaned_data.get('ref_no')
				project.name = form.cleaned_data.get('name')
				project.start_date = form.cleaned_data.get('start_date')
				project.end_date = form.cleaned_data.get('end_date')
				project.save()

				set_message(request, u'แก้ไขโครงการเรียบร้อย')
				return redirect('view_project_overview', (project.id))

		else:
			form = ModifyProjectForm(initial={'parent_project_id':project.parent_project.id, 'project_id':project.id, 'ref_no':project.ref_no, 'name':project.name, 'start_date':project.start_date, 'end_date':project.end_date})

		return render_response(request, 'page_project/project_projects_edit.html', {'project':project, 'form':form})

	else:
		return redirect('view_project_projects', (project.id))

@login_required
def view_project_delete(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	head_project = project.parent_project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if Activity.objects.filter(project=project).count():
			set_message(request, 'ยังมีกิจกรรมอยู่ภายใต้โครงการ ต้องลบกิจกรรมก่อนลบโครงการ')
			return redirect('view_project_overview', (project.id))
		else:
			project.delete()
			set_message(request, u'ลบโครงการเรียบร้อย')
			return redirect('view_project_projects', (head_project.id))

	else:
		return redirect('view_project_projects', (head_project.id))

	return render_response(request, 'page_project/project_projects_edit.html', {'project':project, 'form':form})

@login_required
def view_project_activities(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	current_date = date.today()

	activities = Activity.objects.filter(project=project).order_by('-start_date')

	# Find activities in past month, current month and next month.
	num = 3
	prev_month_ = utilities.get_prev_month(current_date.year, current_date.month, num)
	start = date(prev_month_[0], prev_month_[1], 1)
	next_month_ = utilities.get_next_month(current_date.year, current_date.month, num)
	end = date(next_month_[0], next_month_[1], day=calendar.monthrange(next_month_[0], next_month_[1])[1])
	
	prev_month_ = '%04d%02d' % utilities.get_prev_month(current_date.year, current_date.month)
	next_month_ = '%04d%02d' % utilities.get_next_month(current_date.year, current_date.month)

	recent_activities = Activity.objects.filter(project=project).filter( \
		Q(start_date__lte=start) & Q(end_date__gte=end) | \
		Q(start_date__lte=end) & Q(start_date__gte=start) | \
		Q(end_date__lte=end) & Q(end_date__gte=start))

	return render_response(request, 'page_project/project_activities.html', {'project':project, 'activities':activities, 'recent_activities':recent_activities,'prev_month':prev_month_,'next_month':next_month_})

@login_required
def view_activity_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if request.method == 'POST':
			form = ActivityForm(request.POST)
			if form.is_valid():
				activity = Activity.objects.create(project=project,
					name=form.cleaned_data['name'],
					start_date=form.cleaned_data['start_date'],
					end_date=form.cleaned_data['end_date'],
					description=form.cleaned_data['description'],
					location=form.cleaned_data['location'],
					result_goal=form.cleaned_data['result_goal'],
					result_real=form.cleaned_data['result_real'],
					)

				set_message(request, u'สร้างกิจกรรมเรียบร้อย')

				return redirect('view_activity_overview', (activity.id))

		else:
			form = ActivityForm()

		return render_response(request, 'page_project/project_activity_add.html', {'project':project, 'form':form})

	else:
		return redirect('view_project_activities', (project.id))

#
# ACTIVITY #######################################################################
#
@login_required
def view_activity_overview(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)
	return render_response(request, 'page_activity/activity_overview.html', {'activity':activity,})

@login_required
def view_activity_edit(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)
	project = activity.project

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if request.method == 'POST':
			form = ActivityForm(request.POST)
			if form.is_valid():
				activity.name        = form.cleaned_data['name']
				activity.start_date  = form.cleaned_data['start_date']
				activity.end_date    = form.cleaned_data['end_date']
				activity.description = form.cleaned_data['description']
				activity.location    = form.cleaned_data['location']
				activity.result_goal = form.cleaned_data['result_goal']
				activity.result_real = form.cleaned_data['result_real']
				activity.save()

				set_message(request, u'แก้ไขกิจกรรมเรียบร้อย')

				return redirect('view_activity_overview', (activity.id))

		else:
			form = ActivityForm(initial=activity.__dict__)

		return render_response(request, 'page_activity/activity_edit.html', {'activity':activity, 'form':form})

	else:
		return redirect('view_activity_overview', (activity.id))

@login_required
def view_activity_delete(request, activity_id):
	activity = Activity.objects.get(pk=activity_id)
	project = activity.project

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		activity.delete()
		set_message(request, 'ลบกิจกรรมเรียบร้อย')

	return redirect('/project/%d/activities/' % project.id)
