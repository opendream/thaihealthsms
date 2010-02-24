# -*- encoding: utf-8 -*-
from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from comments.models import Comment
from domain.models import Sector, MasterPlan, Project

from helper import utilities
from helper.message import set_message
from helper.shortcuts import render_response

# SECTOR MANAGE KPI

@login_required
def view_sector_manage_kpi(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	category_list = KPI.objects.filter(master_plan=None).values('category').distinct()
	
	org_kpis = list()
	for category_id in category_list:
		category = KPICategory.objects.get(pk=category_id['category'])
		category.kpis = KPI.objects.filter(master_plan=None, category=category).order_by('ref_no')
		
		org_kpis.append(category)
	
	sector_kpis = list()
	
	current_date = date.today().replace(day=1)
	master_plans = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
	
	has_master_plan_kpis = False
	for master_plan in master_plans:
		category_list = KPI.objects.filter(master_plan=master_plan).values('category').distinct()
		
		if category_list: has_master_plan_kpis = True
		
		kpi_categories = list()
		for category_id in category_list:
			category = KPICategory.objects.get(pk=category_id['category'])
			category.kpis = KPI.objects.filter(master_plan=master_plan, category=category).order_by('ref_no')
			
			for kpi in category.kpis:
				kpi.has_child = KPISchedule.objects.filter(kpi=kpi).count() > 0
			
			kpi_categories.append(category)
		
		master_plan.kpi_categories = kpi_categories
	
	return render_response(request, "page_sector/sector_manage_kpi.html", {'sector':sector, 'org_kpis':org_kpis, 'master_plans':master_plans, 'has_master_plan_kpis':has_master_plan_kpis})

@login_required
def view_sector_add_kpi(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyKPIForm(request.POST, sector=sector)
		if form.is_valid():
			master_plan = form.cleaned_data['master_plan']
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			category = form.cleaned_data['category']
			unit_name = form.cleaned_data['unit_name']
			visible_to_project = form.cleaned_data['visible_to_project']
			
			kpi = KPI.objects.create(ref_no=ref_no,\
				name=name,\
				category=category,\
				unit_name=unit_name,\
				master_plan=master_plan,\
				is_visible_to_project=visible_to_project,\
				created_by=request.user.get_profile())
			
			set_message(request, u"สร้างตัวชี้วัดเรียบร้อย")

			return redirect('view_sector_manage_kpi', (sector_id))
	else:
		form = ModifyKPIForm(sector=sector)
	
	return render_response(request, "page_sector/sector_manage_modify_kpi.html", {'sector':sector, 'form':form})

@login_required
def view_sector_edit_kpi(request, kpi_id):
	kpi = get_object_or_404(KPI, pk=kpi_id)
	sector = kpi.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyKPIForm(request.POST, sector=sector)
		if form.is_valid():
			master_plan = form.cleaned_data['master_plan']
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			category = form.cleaned_data['category']
			unit_name = form.cleaned_data['unit_name']
			visible_to_project = form.cleaned_data['visible_to_project']
			
			kpi.ref_no = ref_no
			kpi.name = name
			kpi.category = category
			kpi.unit_name = unit_name
			kpi.is_visible_to_project = visible_to_project
			kpi.save()
			
			set_message(request, u"แก้ไขตัวชี้วัดเรียบร้อย")

			return redirect('view_sector_manage_kpi', (sector.id))
		
	else:
		form = ModifyKPIForm(sector=sector, initial={'ref_no':kpi.ref_no, 'name':kpi.name, 'category':kpi.category, 'unit_name':kpi.unit_name, 'visible_to_project':kpi.is_visible_to_project})
	
	return render_response(request, "page_sector/sector_manage_modify_kpi.html", {'sector':sector, 'kpi':kpi, 'form':form, })

@login_required
def view_sector_delete_kpi(request, kpi_id):
	kpi = get_object_or_404(KPI, pk=kpi_id)
	sector = kpi.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	if not KPISchedule.objects.filter(kpi=kpi).count():
		kpi.delete()
		set_message(request, u"ลบตัวชี้วัดเรียบร้อย")
	else:
		set_message(request, u"ไม่สามารถลบตัวชี้วัดได้ เนื่องจากมีแผนงานที่ผูกกับตัวชี้วัดนี้อยู่")
	
	return redirect('view_sector_manage_kpi', (sector.id))

@login_required
def view_sector_edit_project_kpi(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	sector = project.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	existing_kpis = KPISchedule.objects.filter(project=project).values('kpi').distinct()
	project_kpis = list()
	for existing_kpi in existing_kpis:
		kpi = KPI.objects.get(pk=existing_kpi['kpi'])
		kpi.schedules = KPISchedule.objects.filter(project=project, kpi=kpi).order_by('target_on')
		project_kpis.append(kpi)
	
	if request.method == 'POST':
		# 'schedule' - kpi_id , schedule_id , target , target_on - "123,None,100,2010-01-01"
		
		schedules = request.POST.getlist('schedule')
		for schedule in schedules:
			print schedule
			(kpi_id, schedule_id, target, target_on) = schedule.split(',')
			(target_on_year, target_on_month, target_on_day) = target_on.split('-')
			target_on = date(int(target_on_year), int(target_on_month), int(target_on_day))
			
			kpi = KPI.objects.get(pk=kpi_id)
			
			if schedule_id and schedule_id != 'None':
				schedule = KPISchedule.objects.get(pk=schedule_id)
				schedule.target = target
				schedule.target_on = target_on
				schedule.save()
			else:
				KPISchedule.objects.create(kpi=kpi, project=project, target=target, result=0, target_on=target_on)
		
		return redirect('view_sector_edit_project_kpi', (project.id))
	
	# Create kpi choice and remove existing kpi from the choices
	kpi_choices = KPI.objects.filter(Q(master_plan=None) | Q(master_plan=project.master_plan)).order_by('category', 'ref_no')
	kpi_choices = [kpi for kpi in kpi_choices if kpi not in project_kpis]
	
	return render_response(request, 'page_sector/sector_manage_edit_project_kpi.html', {'sector':sector, 'project':project, 'kpi_choices':kpi_choices, 'project_kpis':project_kpis})

# MASTER PLAN KPI

@login_required
def view_master_plan_kpi(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	
	current_year = utilities.master_plan_current_year_number(master_plan)
	years = (current_year+543-1, current_year+543)
	
	from functions import get_kpi_project_by_category
	
	kpi_categories = list()
	for category in KPISchedule.objects.filter(kpi__master_plan=None, project__master_plan=master_plan).values('kpi__category').distinct():
		kpi_category = KPICategory.objects.get(pk=category['kpi__category'])
		kpi_category.kpis = get_kpi_project_by_category(kpi_category, master_plan, True)
		kpi_categories.append(kpi_category)

	for category in KPI.objects.filter(master_plan=master_plan).values('category').distinct():
		kpi_category = KPICategory.objects.get(pk=category['category'])
		kpi_category.kpis = get_kpi_project_by_category(kpi_category, master_plan, False)
		kpi_categories.append(kpi_category)
	
	master_plan.categories = kpi_categories
	
	return render_response(request, "page_master_plan/master_plan_kpi.html", {'master_plan':master_plan, 'years':years})

# PROJECT KPI

@login_required
def view_project_kpi(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	
	categories = KPISchedule.objects.filter(project=project, kpi__is_visible_to_project=True).values('kpi__category').distinct()
	
	kpi_categories = list()
	for category in categories:
		category = KPICategory.objects.get(pk=category['kpi__category'])
		kpi_ids = KPISchedule.objects.filter(project=project, kpi__category=category).order_by('kpi__ref_no').values('kpi').distinct()
		
		kpi_category = list()
		
		for kpi_id in kpi_ids:
			kpi = KPI.objects.get(id=kpi_id['kpi'])
			kpi.schedules = KPISchedule.objects.filter(kpi=kpi, project=project).order_by('-target_on')
			
			for schedule in kpi.schedules:
				schedule.comments = Comment.objects.filter(object_name='kpi', object_id=schedule.id).count()
				schedule.revisions = KPIScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
			
			kpi_category.append(kpi)
		
		category.kpi = kpi_category
		
		kpi_categories.append(category)
	
	return render_response(request, "page_project/project_kpi.html", {'project':project, 'kpi_categories':kpi_categories})

# KPI OVERVIEW

@login_required
def view_kpi_overview(request, kpi_schedule_id):
	kpi_schedule = KPISchedule.objects.get(pk=kpi_schedule_id)
	
	if request.method == 'POST':
		form = ModifyKPIRemarkForm(request.POST)
		if form.is_valid():
			remark = form.cleaned_data['remark']
			
			kpi_schedule.remark = form.cleaned_data['remark']
			kpi_schedule.save()
			
			return redirect('view_kpi_overview', (kpi_schedule.id))
		
	else:
		form = ModifyKPIRemarkForm(initial={'remark':kpi_schedule.remark})
	
	revisions = KPIScheduleRevision.objects.filter(schedule=kpi_schedule).order_by('-revised_on')
	
	from helper.utilities import get_kpi_revised_list
	for revision in revisions:
		revision.list = get_kpi_revised_list(revision)
	
	from comments.functions import read_visible_comments
	comments = read_visible_comments(request, 'kpi', kpi_schedule.id)
	
	return render_response(request, 'page_kpi/kpi_overview.html', {'kpi_schedule':kpi_schedule, 'comments':comments, 'revisions':revisions, 'form':form})
