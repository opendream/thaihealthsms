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