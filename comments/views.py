from datetime import datetime

from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import simplejson

from comments.models import *
from domain.models import Activity, UserAccount, Project, UserRoleResponsibility
from report.models import ReportSchedule

from thaihealthsms.helper.utilities import format_abbr_date

@login_required
def ajax_post_object_comment(request, object_name, object_id):
	if request.method == "POST":
		if object_name not in ('activity', 'project', 'report'): raise Http404

		message = request.POST['message'].strip()
		comment = Comment.objects.create(message=message, object_id=object_id, object_name=object_name, \
			sent_by=request.user.get_profile())
		
		comment_receiver_roles = CommentReceiverRole.objects.filter(object_name=object_name)
		roles = [r.role for r in comment_receiver_roles]

		if object_name == 'activity':
			activity = Activity.objects.get(pk=object_id)
			if activity.project.parent_project:
				target_project = activity.project.parent_project
			else:
				target_project = activity.project
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(target_project,))
		
		elif object_name == 'project':
			project = Project.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(project,))

		elif object_name == 'report':
			report_schedule = ReportSchedule.objects.get(pk=object_id)
			if report_schedule.report_project.project.parent_project:
				target_project = report_schedule.report_project.project.parent_project
			else:
				target_project = report_schedule.report_project.project
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(target_project,))

		for r in role_resps:
			CommentReceiver.objects.create(comment=comment, receiver=r.user, sent_on=comment.sent_on)

		receivers = request.POST.getlist('to')
		for receiver in receivers:
			CommentReceiver.objects.create(comment=comment, receiver=UserAccount(id=receiver), sent_on=comment.sent_on)
		
		# TODO: Send Email
		
		return HttpResponse(simplejson.dumps({'id': comment.id,}))
		
	else:
		raise Http404

@login_required
def ajax_reply_comment(request, comment_id):
	if request.method == "POST":
		try:
			comment = Comment.objects.get(pk=comment_id)
		except Comment.DoesNotExist:
			return HttpResponse(simplejson.dumps({'error': '404',}))

		if comment:
			message = request.POST['message'].strip()
			comment_reply = CommentReply.objects.create(comment=comment, content=message, sent_by=request.user.get_profile())

			for receiver in comment.commentreceiver_set.all():
				if receiver.is_read:
					receiver.is_read = False
					receiver.save()

			# TODO: Send Email

			return HttpResponse(simplejson.dumps({'id': comment_reply.id,}))
		else:
			return HttpResponse(simplejson.dumps({'error': '404',}))
	else:
		raise Http404

def ajax_query_comment_receivers(request):
	query_string = request.GET['tag']
	
	users = UserAccount.objects.filter(Q(first_name__istartswith=query_string) | Q(last_name__istartswith=query_string))
	
	receivers = list()
	for user in users:
		receivers.append({'value':user.id, 'caption':user.first_name+" "+user.last_name})
	
	return HttpResponse(simplejson.dumps(receivers))
