from models import *

def retrieve_visible_comments(request, object_name, object_id):
	user_account = request.user.get_profile()
	received_comments = CommentReceiver.objects.filter(\
		receiver=request.user.get_profile(),\
		comment__object_name=object_name, \
		comment__object_id=object_id).order_by('-comment__sent_on')
	
	comments = list()
	for received_comment in received_comments:
		comment = received_comment.comment
		comment.is_read = received_comment.is_read
		
		received_reply_comments = CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(), reply__comment=comment).order_by('reply__sent_on')
		
		replies = list()
		for received_reply_comment in received_reply_comments:
			reply = received_reply_comment.reply
			reply.is_read = received_reply_comment.is_read
			replies.append(reply)
		
		comment.replies = replies
		
		comments.append(comment)
	
	return comments

from domain.models import Activity, Project
from report.models import ReportSchedule

def get_comment_object(object_name, object_id):
	if object_name == 'activity':
		object = Activity.objects.get(pk=object_id)

	elif object_name == 'project':
		object = Project.objects.get(pk=object_id)

	elif object_name == 'report':
		object = ReportSchedule.objects.get(pk=object_id)
		
	else:
		object = None
	
	return object
