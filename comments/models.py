from django.db import models

class Comment(models.Model):
	message = models.CharField(max_length=1024)
	object_id = models.IntegerField(default=0)
	object_name = models.CharField(max_length=64, null=True)
	is_private = models.BooleanField(default=True)
	is_urgent = models.BooleanField(default=False)
	sent_on = models.DateTimeField(auto_now_add=True)
	sent_by = models.ForeignKey('domain.UserAccount')

class CommentReceiver(models.Model):
	comment = models.ForeignKey('Comment')
	receiver = models.ForeignKey('domain.UserAccount')
	is_read = models.BooleanField(default=False)
	sent_on = models.DateTimeField() # Save value as in Comment

class CommentReply(models.Model):
	comment = models.ForeignKey('Comment')
	content = models.CharField(max_length=1024)
	sent_on = models.DateTimeField(auto_now_add=True)
	sent_by = models.ForeignKey('domain.UserAccount')



"""
class ReportComment(models.Model):
	report = models.ForeignKey('report.ReportSchedule')
	comment = models.CharField(max_length=1024)
	commented_on = models.DateTimeField(auto_now_add=True)
	commented_by = models.ForeignKey('domain.UserAccount')

class ProjectComment(models.Model):
	project = models.ForeignKey('domain.Project')
	comment = models.CharField(max_length=1024)
	commented_on = models.DateTimeField(auto_now_add=True)
	commented_by = models.ForeignKey('domain.UserAccount')

class ActivityComment(models.Model):
	activity = models.ForeignKey('domain.Activity')
	comment = models.CharField(max_length=1024)
	commented_on = models.DateTimeField(auto_now_add=True)
	commented_by = models.ForeignKey('domain.UserAccount')

class KPIComment(models.Model):
	kpi = models.ForeignKey('domain.ProjectKPI')
	comment = models.CharField(max_length=1024)
	commented_on = models.DateTimeField(auto_now_add=True)
	commented_by = models.ForeignKey('domain.UserAccount')

#class FinanceComment(models.Model):
#	report = models.ForeignKey('report.ReportSchedule')
#	comment = models.CharField(max_length=1024)
#	commented_on = models.DateTimeField(auto_now_add=True)
#	commented_by = models.ForeignKey('domain.UserAccount')
"""
