# -*- encoding: utf-8 -*-

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper.utilities import format_abbr_date, responsible

@login_required
def ajax_update_finance_value(request):
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
		
		finance_schedule = ProjectBudgetSchedule.objects.get(pk=schedule_id)
		
		if responsible(request.user, 'sector_manager_assistant', finance_schedule.project):
			revision = ProjectBudgetScheduleRevision.objects.create(
				schedule=finance_schedule,
				org_target=finance_schedule.target,
				org_result=finance_schedule.result,
				org_target_on=finance_schedule.target_on,
				new_target=finance_schedule.target,
				new_result=result,
				new_target_on=finance_schedule.target_on,
				revised_by=request.user.get_profile()
			)
			
			finance_schedule.result = result
			finance_schedule.save()
			
			from helper.utilities import get_finance_revision_html
			return HttpResponse(simplejson.dumps({'revision_html':'<li>' + get_finance_revision_html(revision) + '</li>'}))
		
		else:
			raise Http404
	else:
		raise Http404

@login_required
def ajax_claim_finance_schedule(request):
	if request.method == 'POST':
		schedule_id = request.POST.get('schedule_id')
		result = request.POST.get('claim_amount', '0')
		claim_on = request.POST.get('claim_on', '')
		
		finance_schedule = ProjectBudgetSchedule.objects.get(pk=schedule_id)
		
		if not responsible(request.user, 'sector_manager_assistant', finance_schedule.project): raise Http404
		
		if claim_on:
			try:
				date_split = claim_on.split('-')
				claimed_on = date(int(date_split[0]), int(date_split[1]), int(date_split[2]))
			except:
				return HttpResponse(simplejson.dumps({'error':'invalid'}))
		
		try:
			result = int(result)
		except:
			return HttpResponse(simplejson.dumps({'error':'invalid'}))
		
		finance_schedule.claimed_on = claimed_on
		finance_schedule.result = result
		finance_schedule.save()
		
		return HttpResponse(simplejson.dumps({'claim_html':unicode('<div class="claimed">เบิกจ่ายไปเมื่อวันที่ %s เป็นจำนวนเงิน %d บาท</div>', 'utf-8') % (format_abbr_date(finance_schedule.claimed_on), finance_schedule.result)}))
	
	else:
		raise Http404
