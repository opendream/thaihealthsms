from datetime import datetime

from django.conf import settings
from django.core.mail import send_mass_mail
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.utils import simplejson

from functions import get_comment_object, comment_count
from models import *

from accounts.models import UserAccount, UserRoleResponsibility
from domain.models import Activity, Project
from report.models import ReportSchedule
from kpi.models import KPISchedule
from finance.models import ProjectBudgetSchedule

from helper.utilities import format_abbr_date

@login_required
def ajax_post_object_comment(request, object_name, object_id):
	if request.method == "POST":
		if object_name not in ('activity', 'project', 'report', 'kpi', 'finance'): raise Http404
		
		message = request.POST['message'].strip()
		
		comment_receiver_roles = CommentReceiverRole.objects.filter(object_name=object_name)
		roles = [r.role for r in comment_receiver_roles]
		
		if object_name == 'activity':
			activity = Activity.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(activity.project.parent_project,))
		
		elif object_name == 'project':
			project = Project.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(project.parent_project,))
		
		elif object_name == 'report':
			report_schedule = ReportSchedule.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(report_schedule.report_project.project,))
		
		elif object_name == 'kpi':
			kpi_schedule = KPISchedule.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(kpi_schedule.project,))
		
		elif object_name == 'finance':
			finance_schedule = ProjectBudgetSchedule.objects.get(pk=object_id)
			role_resps = UserRoleResponsibility.objects.filter(role__in=(roles), projects__in=(finance_schedule.project,))
		
		if not role_resps:
			return HttpResponse(simplejson.dumps({'id':0}));
			
		else:
			comment = Comment.objects.create(message=message, object_id=object_id, object_name=object_name, sent_by=request.user.get_profile())
			
			email_recipient_list = list()
			
			for r in role_resps:
				if r.user != request.get_profile():
					CommentReceiver.objects.create(comment=comment, receiver=r.user)
					email_recipient_list.append(r.user.user.email)
			
			CommentReceiver.objects.create(comment=comment, receiver=request.user.get_profile(), is_read=True) # Create receiver record for sender
			
			object = get_comment_object(comment.object_name, comment.object_id)
			
			email_render_dict = {'comment':comment, 'object':object, 'site':Site.objects.get_current()}
			email_subject = render_to_string('email/notify_comment_subject.txt', email_render_dict)
			email_message = render_to_string('email/notify_comment_message.txt', email_render_dict)
			
			datatuple = ((email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, email_recipient_list),)
			
			send_mass_mail(datatuple, fail_silently=True)
			
			return HttpResponse(simplejson.dumps({'id':comment.id, 'object_id':object_id, 'object_name':object_name, 'count':comment_count(object_name, object_id)}))
		
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
			
			email_recipient_list = list()
			
			for receiver in comment.receivers.all():
				if receiver.id == request.user.get_profile().id:
					CommentReplyReceiver.objects.create(reply=comment_reply, receiver=receiver, is_read=True)
				else:
					CommentReplyReceiver.objects.create(reply=comment_reply, receiver=receiver)
					email_recipient_list.append(receiver.user.email)
			
			object = get_comment_object(comment_reply.comment.object_name, comment_reply.comment.object_id)
			
			email_render_dict = {'comment':comment_reply.comment, 'comment_reply':comment_reply, 'object':object, 'site':Site.objects.get_current()}
			email_subject = render_to_string('email/notify_comment_reply_subject.txt', email_render_dict)
			email_message = render_to_string('email/notify_comment_reply_message.txt', email_render_dict)
			
			datatuple = ((email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, email_recipient_list),)
			
			send_mass_mail(datatuple, fail_silently=True)
			
			return HttpResponse(simplejson.dumps({'id': comment_reply.id,
				'first_name':comment_reply.sent_by.first_name,
				'last_name':comment_reply.sent_by.last_name,
				'date_timestamp':format_abbr_date(comment_reply.sent_on),
				'time_timestamp':'%02d:%02d' % (comment_reply.sent_on.hour, comment_reply.sent_on.minute),}))
		
		else:
			return HttpResponse(simplejson.dumps({'error': '404',}))
	else:
		raise Http404