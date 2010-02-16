
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from helper.shortcuts import render_response, access_denied

from domain.models import Project, Activity
from report.models import ReportSchedule

from comments.models import *
from comments.functions import retrieve_visible_comments, get_comment_object

@login_required
def view_dashboard_comments(request):
	user_account = request.user.get_profile()

	comments = set()
	for received_comment in CommentReceiver.objects.filter(is_read=False, receiver=user_account):
		comments.add(received_comment.comment)

	for received_comment in CommentReplyReceiver.objects.filter(is_read=False, receiver=user_account):
		comments.add(received_comment.reply.comment)

	comment_list = list(comments)
	comment_list.sort(_comments_sorting, reverse=True)

	for comment in comment_list:
		comment.is_read = CommentReceiver.objects.get(comment=comment, receiver=user_account).is_read
		
		receivers = CommentReplyReceiver.objects.filter(is_read=False, reply__comment=comment, receiver=user_account).order_by('reply__sent_on')
		replies = list()
		for receiver in receivers:
			replies.append(receiver.reply)
		comment.replies = replies

	object_list = list()
	object_dict = dict()

	for comment in comment_list:
		hash_str = "%s%d" % (comment.object_name, comment.object_id)
		if hash_str not in object_list:
			object = get_comment_object(comment.object_name, comment.object_id)

			if object:
				object_list.append(hash_str)
				object_dict[hash_str] = {'comment':comment, 'object':object, 'comments':[comment]}

		else:
			object_dict[hash_str]['comments'].append(comment)

	objects = list()
	for object_hash in object_list:
		objects.append(object_dict[object_hash])

	return render_response(request, "page_dashboard/dashboard_comments.html", {'objects':objects})

def _comments_sorting(x, y):
	return cmp(x.sent_on, y.sent_on)

@login_required
def view_project_comments(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	comments = retrieve_visible_comments(request, 'project', project.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='project',\
		comment__object_id=project.id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='project',\
		reply__comment__object_id=project.id).update(is_read=True)

	return render_response(request, "page_project/project_comments.html", {'project':project, 'comments':comments})

@login_required
def view_activity_comments(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)

	comments = retrieve_visible_comments(request, 'activity', activity.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='activity', \
		comment__object_id=activity_id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='activity',\
		reply__comment__object_id=activity_id).update(is_read=True)

	return render_response(request, "page_activity/activity_comments.html", {'activity':activity, 'comments':comments,})

@login_required
def view_report_comments(request, report_id):
	report = get_object_or_404(ReportSchedule, pk=report_id)

	comments = retrieve_visible_comments(request, 'report', report.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(),\
		comment__object_name='report',\
		comment__object_id=report.id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='report',\
		reply__comment__object_id=report.id).update(is_read=True)

	return render_response(request, "page_report/report_comments.html", {'report_schedule':report, 'comments':comments, })
