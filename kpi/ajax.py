# -*- encoding: utf-8 -*-

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper.utilities import responsible

@login_required
def ajax_update_kpi_value(request):
	if request.method == 'POST':
		schedule_id = request.POST.get('schedule_id')
		target_on = request.POST.get('target_on', '')
		target = request.POST.get('target', '0')
		result = request.POST.get('result', '0')
		
		if target_on:
			try:
				date_split = target_on.split('-')
				target_on = date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
			except:
				return HttpResponse(simplejson.dumps({'error':'invalid'}))
		
		try:
			target = int(target)
		except:
			target = None
		
		try:
			result = int(result)
		except:
			return HttpResponse(simplejson.dumps({'error':'invalid'}))
		
		kpi_schedule = KPISchedule.objects.get(pk=schedule_id)
		
		if responsible(request.user, 'sector_manager_assistant', kpi_schedule.project):
			
			if not target_on: target_on = kpi_schedule.target_on
			if not target: target = kpi_schedule.target
			if not result: result = kpi_schedule.result
			
			revision = KPIScheduleRevision.objects.create(
				schedule=kpi_schedule,
				org_target=kpi_schedule.target,
				org_result=kpi_schedule.result,
				org_target_on=kpi_schedule.target_on,
				new_target=target,
				new_result=result,
				new_target_on=target_on,
				revised_by=request.user.get_profile()
			)
			
			kpi_schedule.target_on = target_on
			kpi_schedule.target = target
			kpi_schedule.result = result
			kpi_schedule.save()
			
			from helper.utilities import get_kpi_revision_html
			return HttpResponse(simplejson.dumps({'revision_html':'<li>' + get_kpi_revision_html(revision) + '</li>'}))
		
		elif responsible(request.user, 'project_manager,project_manager_assistant', kpi_schedule.project):
			
			target_on = kpi_schedule.target_on # PM cannot change target_on
			target = kpi_schedule.target # PM cannot change target
			if not result: result = kpi_schedule.result
			
			revision = KPIScheduleRevision.objects.create(
				schedule=kpi_schedule,
				org_target=kpi_schedule.target,
				org_result=kpi_schedule.result,
				org_target_on=kpi_schedule.target_on,
				new_target=target,
				new_result=result,
				new_target_on=target_on,
				revised_by=request.user.get_profile()
			)
			
			kpi_schedule.target_on = target_on
			kpi_schedule.target = target
			kpi_schedule.result = result
			kpi_schedule.save()
			
			from helper.utilities import get_kpi_revision_html
			return HttpResponse(simplejson.dumps({'revision_html':'<li>' + get_kpi_revision_html(revision) + '</li>'}))
		
		raise Http404
		
	else:
		raise Http404

