from datetime import date

from django.db.models import F

from models import ProjectBudgetSchedule, ProjectBudgetScheduleRevision

from domain.models import Project

from helper import utilities

def overview_master_plan_finance(master_plan):
	start_date, end_date = utilities.master_plan_current_year_span(master_plan)
	projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
	budget_schedules = ProjectBudgetSchedule.objects.filter(project__in=projects, target_on__gte=start_date, target_on__lte=end_date)
	
	all_target = sum_target = sum_result = 0.0
	for budget_schedule in budget_schedules:
		all_target += budget_schedule.target
		if budget_schedule.target_on <= date.today():
			sum_target += budget_schedule.target
			sum_result += budget_schedule.result
	
	master_plan.sum_target = int(sum_target)
	master_plan.sum_result = int(sum_result)
	master_plan.all_target = int(all_target)
	
	if all_target > 0.0:
		master_plan.percent_target = int(sum_target/all_target * 100)
		master_plan.percent_result = int(sum_result/all_target * 100)
	else:
		master_plan.all_target = -1
	
	# events
	events = list()
	late_schedules = budget_schedules.filter(claimed_on=None, target_on__lt=date.today())
	
	for schedule in late_schedules:
		events.append({'date':schedule.target_on, 'type':'late', 'data':schedule})
	
	postpone_revisions = ProjectBudgetScheduleRevision.objects.filter(schedule__in=budget_schedules).exclude(org_target_on=F('new_target_on'))
	
	for revision in postpone_revisions:
		revised_date = date(revision.revised_on.year, revision.revised_on.month, revision.revised_on.day)
		events.append({'date':revised_date, 'type':'postpone', 'data':revision})
	
	events.sort(sort_events, reverse=True)
	
	master_plan.events = events
	
	return master_plan

def overview_project_finance(project):
	start_date, end_date = utilities.master_plan_current_year_span(project.master_plan)
	
	events = list()
	late_schedules = ProjectBudgetSchedule.objects.filter(project=project, target_on__gte=start_date, target_on__lte=end_date, claimed_on=None, target_on__lt=date.today())
	
	for schedule in late_schedules:
		events.append({'date':schedule.target_on, 'type':'late', 'data':schedule})
	
	budget_schedules = ProjectBudgetSchedule.objects.filter(project=project, target_on__gte=start_date, target_on__lte=end_date)
	postpone_revisions = ProjectBudgetScheduleRevision.objects.filter(schedule__in=budget_schedules).exclude(org_target_on=F('new_target_on'))
	
	for revision in postpone_revisions:
		revised_date = date(revision.revised_on.year, revision.revised_on.month, revision.revised_on.day)
		events.append({'date':revised_date, 'type':'postpone', 'data':revision})
	
	events.sort(sort_events, reverse=True)
	
	return events

def sort_events(x, y):
	return x['date'].toordinal() - y['date'].toordinal()
	
	