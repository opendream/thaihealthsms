from domain.models import UserAccount

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)


from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import simplejson

from helper.utilities import format_display_datetime
from domain.models import KPISubmission, KPISubmissionRevision, FinanceKPISubmission, FinanceKPISubmissionRevision

@login_required
def ajax_update_kpi_submission(request):
	if request.method == "POST":
		submission_id = request.POST.get("submission")
		target = request.POST.get("target")
		result = request.POST.get("result")
		
		submission = KPISubmission.objects.get(pk=submission_id)
		
		revision = KPISubmissionRevision.objects.create(submission=submission, target_score=submission.target_score, result_score=submission.result_score, submitted_by=request.user.get_profile())
		
		submission.target_score = int(target)
		submission.result_score = int(result)
		submission.last_update = revision.submitted_on
		submission.save()
		
		return HttpResponse(simplejson.dumps({'id':submission.id, 'target_score':revision.target_score, 'result_score':revision.result_score, 'submitted_on':format_display_datetime(revision.submitted_on)}))
		
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
