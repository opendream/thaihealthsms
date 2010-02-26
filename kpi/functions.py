# -*- encoding: utf-8 -*-

from datetime import timedelta

from django.db.models import Sum

from models import *
from domain.models import Project
from helper import utilities

def _schedules_percentage(schedules):
	if schedules:
		percentage_sum = 0
		percentage_count = 0
		for schedule in schedules:
			if schedule.target:
				percentage_sum = percentage_sum + int(float(schedule.result) / float(schedule.target) * 100)
				percentage_count = percentage_count + 1
		
		if percentage_count:
			return int(percentage_sum / percentage_count)
		else:
			return -1
		
	else:
		return -1

# Use in sector overview page
def get_kpi_summary_by_category(kpi_category, master_plan, is_organization_kpi):
	if is_organization_kpi:
		kpis = KPI.objects.filter(category=kpi_category, master_plan=None)
	else:
		kpis = KPI.objects.filter(category=kpi_category, master_plan=master_plan)
	
	# Current Year
	(masterplan_start, masterplan_end) = utilities.master_plan_current_year_span(master_plan)
	
	if is_organization_kpi:
		schedules = KPISchedule.objects.filter(kpi__in=kpis, kpi__master_plan=None, project__master_plan=master_plan, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
	else:
		schedules = KPISchedule.objects.filter(kpi__in=kpis, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
	
	kpi_category.current_year = _schedules_percentage(schedules)
	
	# Previous Year
	masterplan_start = masterplan_start.replace(masterplan_start.year - 1)
	masterplan_end = masterplan_end.replace(masterplan_end.year - 1)
	
	if is_organization_kpi:
		schedules = KPISchedule.objects.filter(kpi__in=kpis, kpi__master_plan=None, project__master_plan=master_plan, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
	else:
		schedules = KPISchedule.objects.filter(kpi__in=kpis, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
	
	kpi_category.is_organization_kpi = is_organization_kpi
	kpi_category.previous_year = _schedules_percentage(schedules)
	
	return kpi_category

# Use in master plan kpi page
def get_kpi_project_by_category(kpi_category, master_plan, is_organization_kpi):
	"""
	category.kpis -> kpi
	kpi.years -> year
	kpi.projects -> project
	project.years -> year
	"""
	
	if is_organization_kpi:
		kpis = KPI.objects.filter(category=kpi_category, master_plan=None)
	else:
		kpis = KPI.objects.filter(category=kpi_category, master_plan=master_plan)
	
	(masterplan_start, masterplan_end) = utilities.master_plan_current_year_span(master_plan)
	previous_masterplan_start = masterplan_start.replace(masterplan_start.year - 1)
	previous_masterplan_end = masterplan_end.replace(masterplan_end.year - 1)
	
	for kpi in kpis:
		if is_organization_kpi:
			current_schedules = KPISchedule.objects.filter(kpi=kpi, kpi__master_plan=None, project__master_plan=master_plan, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
			previous_schedules = KPISchedule.objects.filter(kpi=kpi, kpi__master_plan=None, project__master_plan=master_plan, target_on__gte=previous_masterplan_start, target_on__lte=previous_masterplan_end)
			schedule_projects = KPISchedule.objects.filter(kpi=kpi, kpi__master_plan=None, project__master_plan=master_plan).values('project').distinct()
		else:
			current_schedules = KPISchedule.objects.filter(kpi=kpi, target_on__gte=masterplan_start, target_on__lte=masterplan_end)
			previous_schedules = KPISchedule.objects.filter(kpi=kpi, target_on__gte=previous_masterplan_start, target_on__lte=previous_masterplan_end)
			schedule_projects = KPISchedule.objects.filter(kpi=kpi).values('project').distinct()
		
		kpi.years = (_schedules_percentage(previous_schedules), _schedules_percentage(current_schedules), )
		
		projects = list()
		for schedule_project in schedule_projects:
			project = Project.objects.get(pk=schedule_project['project'])
			
			current_schedules = KPISchedule.objects.filter(kpi=kpi, target_on__gte=masterplan_start, target_on__lte=masterplan_end, project=project)
			previous_schedules = KPISchedule.objects.filter(kpi=kpi, target_on__gte=previous_masterplan_start, target_on__lte=previous_masterplan_end, project=project)
			
			project.years = (_schedules_percentage(previous_schedules), _schedules_percentage(current_schedules), )
			projects.append(project)
		
		kpi.projects = projects
	
	return kpis
