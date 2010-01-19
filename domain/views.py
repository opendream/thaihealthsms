from domain.models import UserAccount

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)


from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from helper.utilities import format_display_datetime, user_has_role
from domain.models import ProjectBudgetSchedule
from domain.models import ProjectBudgetScheduleRevision
from domain.models import KPISchedule
from domain.models import KPIScheduleRevision
from domain.models import UserRoleResponsibility

@login_required
def ajax_update_kpi_schedule(request):
	if request.method == "POST":
		schedule_id = request.POST.get("schedule")
		target = request.POST.get("target")
		result = request.POST.get("result")
		
		schedule = KPISchedule.objects.get(pk=schedule_id)
		
		if user_has_role(request.user, ('sector_manager_assistant',)):
			if UserRoleResponsibility.objects.filter(user=request.user, role__name='sector_manager_assistant', projects__in=(schedule.project,)):
				revision = KPIScheduleRevision.objects.create(schedule=schedule, target_score=schedule.target_score, result_score=schedule.result_score, revised_by=request.user.get_profile())
				
				schedule.target_score = int(target)
				schedule.result_score = int(result)
				schedule.last_update = revision.revised_on
				schedule.save()
		
		elif user_has_role(request.user, ('program_manager', 'program_manager_assistant')):
			if UserRoleResponsibility.objects.filter(user=request.user, role__name='program_manager', projects__in=(schedule.project,)) or UserRoleResponsibility.objects.filter(user=request.user, role__name='program_manager_assistant', projects__in=(schedule.project,)):
				revision = KPIScheduleRevision.objects.create(schedule=schedule, target_score=schedule.target_score, result_score=schedule.result_score, revised_by=request.user.get_profile())
				
				schedule.result_score = int(result)
				schedule.last_update = revision.revised_on
				schedule.save()
		
		return HttpResponse(simplejson.dumps({'id':schedule.id, 'target_score':revision.target_score, 'result_score':revision.result_score, 'revised_on':format_display_datetime(revision.revised_on)}))
		
	else:
		raise Http404

@login_required
def ajax_update_finance_schedule(request):
	if request.method == "POST":
		schedule_id = request.POST.get("schedule")
		expected_budget = request.POST.get("expected")
		used_budget = request.POST.get("used")
		
		schedule = ProjectBudgetSchedule.objects.get(pk=schedule_id)
		
		revision = ProjectBudgetScheduleRevision.objects.create(schedule=schedule, expected_budget=schedule.expected_budget, used_budget=schedule.used_budget, revised_by=request.user.get_profile())
		
		schedule.expected_budget = int(expected_budget)
		schedule.used_budget = int(used_budget)
		schedule.save()
		
		return HttpResponse(simplejson.dumps({'id':schedule.id, 'expected':revision.expected_budget, 'used':revision.used_budget, 'revised_on':format_display_datetime(revision.revised_on)}))
		
	else:
		raise Http404
