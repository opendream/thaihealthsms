from models import *

"""
from comments.models import *
from domain.models import *
from report.models import *

def comments_build_attr(comments_dummy, user):
	comments = []
	for comment in comments_dummy:
		profile = comment.commented_by.user.get_profile()
		comment.fullname = profile.first_name + ' ' + profile.last_name
		comment.is_own = comment.commented_by.user == user
		comments += [comment]
	return comments

def prepare_comment(comment_type, comment_type_id, comment_id):
	comment = None
	if comment_id:
		if comment_type == 'report':
			comment = ReportComment.objects.get(pk=comment_id)
		elif comment_type == 'project':
			comment = ProjectComment.objects.get(pk=comment_id)
		elif comment_type == 'activity':
			comment = ActivityComment.objects.get(pk=comment_id)
		elif comment_type == 'kpi':
			comment = KPIComment.objects.get(pk=comment_id)
	else:
		if comment_type == 'report':
			comment = ReportComment()
			comment.report = ReportSchedule.objects.get(pk=comment_type_id)
		elif comment_type == 'project':
			comment = ProjectComment()
			comment.project = Project.objects.get(pk=comment_type_id)
		elif comment_type == 'activity':
			comment = ActivityComment()
			comment.activity = Activity.objects.get(pk=comment_type_id)
		elif comment_type == 'kpi':
			comment = KPIComment()
			comment.kpi = ProjectKPI.objects.get(pk=comment_type_id)
	return comment
"""

def retrieve_visible_comments(request, object_name, object_id):
	user_account = request.user.get_profile()
	comment_replies = CommentReceiver.objects.filter(\
		receiver=request.user.get_profile(),\
		comment__object_name=object_name, \
		comment__object_id=object_id)
	
	received_comments = list()
	for comment_reply in comment_replies:
		comment_reply.comment.is_read = comment_reply.is_read
		received_comments.append(comment_reply.comment)
	
	sent_comments = Comment.objects.filter(object_name=object_name, object_id=object_id, sent_by=user_account)
	
	combined_comments = received_comments
	for comment in sent_comments:
		duplicated = False
		for received_comment in received_comments:
			if received_comment.id == comment.id:
				duplicated = True
		
		if not duplicated:
			comment.is_read = True
			combined_comments.append(comment)
	
	combined_comments.sort(_comments_sorting)
	return combined_comments

def _comments_sorting(x, y):
	return cmp(x.sent_on, y.sent_on)




