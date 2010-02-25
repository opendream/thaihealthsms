# -*- encoding: utf-8 -*-

from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from forms import *
from models import *

from comments.models import Comment, CommentReply
from domain.models import Project

from helper import utilities
from helper.message import set_message
from helper.shortcuts import render_response, access_denied

@login_required
def view_sector_edit_project_finance(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	sector = project.master_plan.sector
	
	if not utilities.responsible(request.user, 'admin,sector_manager_assistant,sector_admin', sector):
		return access_denied(request)
	
	project_schedules = ProjectBudgetSchedule.objects.filter(project=project).order_by('target_on')
	for project_schedule in project_schedules:
		project_schedule.revisions = ProjectBudgetScheduleRevision.objects.filter(schedule=project_schedule)
	
	if request.method == 'POST':
		schedules = request.POST.getlist('schedule')
		updating_schedules = list()
		for schedule in schedules:
			try:
				(schedule_id, target, target_on) = schedule.split(',')
				(target_on_year, target_on_month, target_on_day) = target_on.split('-')
				target_on = date(int(target_on_year), int(target_on_month), int(target_on_day))
				
				target = int(target)
				
			except:
				return render_response(request, 'page_sector/sector_manage_edit_project_finance.html', {'sector':sector, 'project':project, 'schedules':project_schedules})
			
			else:
				if schedule_id and schedule_id != 'None':
					schedule = ProjectBudgetSchedule.objects.get(pk=schedule_id)
					
					revision = ProjectBudgetScheduleRevision.objects.create(
						schedule=schedule,
						org_target=schedule.target,
						org_result=schedule.result,
						org_target_on=schedule.target_on,
						new_target=target,
						new_result=schedule.result,
						new_target_on=target_on,
						revised_by=request.user.get_profile()
					)
					
					schedule.target = target
					schedule.target_on = target_on
					schedule.save()
					
				else:
					schedule = ProjectBudgetSchedule.objects.create(project=project, target=target, result=0, target_on=target_on)
				
				updating_schedules.append(schedule)
		
		# Remove schedule
		for project_schedule in project_schedules:
			found = False
			for schedule in updating_schedules:
				if schedule == project_schedule:
					found = True
			
			if not found:
				ProjectBudgetScheduleRevision.objects.filter(schedule=project_schedule).delete()
				
				comments = Comment.objects.filter(object_name='finance', object_id=project_schedule.id)
				CommentReply.objects.filter(comment__in=comments).delete()
				comments.delete()
				
				project_schedule.delete()
		
		return redirect('view_sector_edit_project_finance', (project.id))
	
	return render_response(request, 'page_sector/sector_manage_edit_project_finance.html', {'sector':sector, 'project':project, 'schedules':project_schedules})

@login_required
def view_project_finance(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	
	schedules = ProjectBudgetSchedule.objects.filter(project=project).order_by('-target_on')
	
	for schedule in schedules:
		schedule.revisions = ProjectBudgetScheduleRevision.objects.filter(schedule=schedule).order_by('-revised_on')
	
	return render_response(request, 'page_project/project_finance.html', {'project':project, 'schedules':schedules})

# FINANCE OVERVIEW

@login_required
def view_finance_overview(request, finance_schedule_id):
	finance_schedule = ProjectBudgetSchedule.objects.get(pk=finance_schedule_id)
	
	if request.method == 'POST':
		form = ModifyFinanceRemarkForm(request.POST)
		if form.is_valid():
			remark = form.cleaned_data['remark']
			
			finance_schedule.remark = form.cleaned_data['remark']
			finance_schedule.save()
			
			return redirect('view_finance_overview', (finance_schedule.id))
		
	else:
		form = ModifyFinanceRemarkForm(initial={'remark':finance_schedule.remark})
	
	revisions = ProjectBudgetScheduleRevision.objects.filter(schedule=finance_schedule).order_by('-revised_on')
	
	from helper.utilities import get_finance_revised_list
	for revision in revisions:
		revision.list = get_finance_revised_list(revision)
	
	from comments.functions import read_visible_comments
	comments = read_visible_comments(request, 'finance', finance_schedule.id)
	
	return render_response(request, 'page_kpi/finance_overview.html', {'finance_schedule':finance_schedule, 'comments':comments, 'revisions':revisions, 'form':form})
