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
def ajax_post_user_comment(request, user_id):
	if request.method == "POST":
		message = request.POST['message'].strip()
		comment = Comment.objects.create(message=message, sent_by=request.user.get_profile())
		
		receivers = request.POST.getlist('to')
		for receiver in receivers:
			CommentReceiver.objects.create(comment=comment, receiver=UserAccount(id=receiver), sent_on=comment.sent_on)
		
		# TODO: Send Email
		
		return HttpResponse(simplejson.dumps({'id': comment.id,}))
		
	else:
		raise Http404

@login_required
def ajax_post_object_comment(request, object_name, object_id):
	if request.method == "POST":
		if object_name not in ('activity', 'project', 'program', 'report'): raise Http404

		message = request.POST['message'].strip()
		comment = Comment.objects.create(message=message, object_id=object_id, object_name=object_name, sent_by=request.user.get_profile())
		
		if object_name == "activity":
			activity = Activity.objects.get(pk=object_id)
		
		elif object_name == "project":
			project = Project.objects.get(pk=object_id)

		elif object_name == "program":
			project = Project.objects.get(pk=object_id)

		elif object_name == "report":
			report_schedule = ReportSchedule.objects.get(pk=object_id)

		comment_receiver_roles = CommentReceiverRole.objects.filter(object_name=object_name)
		roles = [r.role for r in comment_receiver_roles]
		role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(project,))
		for r in role_resps:
			CommentReceiver.objects.create(comment=comment, receiver=r.user, sent_on=comment.sent_on)

		# TESTING PURPOSE ONLY!!!!
		# CommentReceiver.objects.create(comment=comment, receiver=request.user.get_profile(), sent_on=comment.sent_on)
		
		receivers = request.POST.getlist('to')
		for receiver in receivers: CommentReceiver.objects.create(comment=comment, receiver=UserAccount(id=receiver), sent_on=comment.sent_on)
		
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
			#comment_reply = CommentReply.objects.create(comment=comment, message=message, sent_by=request.user.get_profile())

			# TODO: Send Email

			#return HttpResponse(simplejson.dumps({'id': comment_reply.id,}))
			return HttpResponse(simplejson.dumps({'id': comment.id,}))
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
	
	
	

"""
def view_comment_save(request, comment_type, comment_type_id, comment_id):
	text = request.POST.get('comment')
	text = text.strip()
	comment = prepare_comment(comment_type, comment_type_id, comment_id)
	if not comment or not text: return
	comment.comment = text
	comment.commented_by = UserAccount.objects.get(user=request.user)
	comment.save()
	
	fullname = request.user.get_profile().first_name + ' ' + request.user.get_profile().last_name
	
	# TODO : Send notification email
	
	return HttpResponse(simplejson.dumps({
		'id': comment.id, 
		'fullname': fullname, 
		'date_timestamp': format_abbr_date(comment.commented_on),
		'time_timestamp': comment.commented_on.strftime('%H:%M'),
	}))

def view_comment_delete(request, comment_type, comment_id):
	comment = prepare_comment(comment_type, 0, comment_id)
	comment.delete()
	return HttpResponse(simplejson.dumps({
		'message': 'Success', 
	}))
"""
