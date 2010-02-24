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
		result = request.POST.get('result', '')
		
		if result:
			try:
				result = int(result)
			except:
				return HttpResponse(simplejson.dumps({'error':'invalid'}))
			
			if result < 0: return HttpResponse(simplejson.dumps({'error':'invalid'}))
		else:
			return HttpResponse(simplejson.dumps({'error':'empty'}))
		
		kpi_schedule = KPISchedule.objects.get(pk=schedule_id)
		
		if responsible(request.user, 'sector_manager_assistant,project_manager,project_manager_assistant', kpi_schedule.project):
			if result == '': result = kpi_schedule.result
			
			revision = KPIScheduleRevision.objects.create(
				schedule=kpi_schedule,
				org_target=kpi_schedule.target,
				org_result=kpi_schedule.result,
				org_target_on=kpi_schedule.target_on,
				new_target=kpi_schedule.target,
				new_result=result,
				new_target_on=kpi_schedule.target_on,
				revised_by=request.user.get_profile()
			)
			
			kpi_schedule.result = result
			kpi_schedule.save()
			
			from helper.utilities import get_kpi_revision_html
			return HttpResponse(simplejson.dumps({'revision_html':'<li>' + get_kpi_revision_html(revision) + '</li>'}))
		
		else:
			raise Http404
	else:
		raise Http404

