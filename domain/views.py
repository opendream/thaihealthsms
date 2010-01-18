from domain.models import UserAccount

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)


from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from helper.utilities import format_display_datetime, user_has_role
from domain.models import ProjectBudgetSchedule, ProjectBudgetScheduleRevision, KPISchedule, KPIScheduleRevision, UserRoleResponsibility

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
def ajax_update_finance_kpi_submission(request):
	if request.method == "POST":
		submission_id = request.POST.get("submission")
		budget = request.POST.get("budget")
		spent = request.POST.get("spent")
		
		submission = FinanceKPISubmission.objects.get(pk=submission_id)
		
		revision = FinanceKPISubmissionRevision.objects.create(submission=submission, budget=submission.budget, spent_budget=submission.spent_budget, submitted_by=request.user.get_profile())
		
		submission.budget = int(budget)
		submission.spent_budget = int(spent)
		submission.last_update = revision.submitted_on
		submission.save()
		
		return HttpResponse(simplejson.dumps({'id':submission.id, 'budget':revision.budget, 'spent_budget':revision.spent_budget, 'submitted_on':format_display_datetime(revision.submitted_on)}))
		
	else:
		raise Http404
