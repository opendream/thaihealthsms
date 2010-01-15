from django.contrib.auth.models import User
from django.db import models

SUBMIT_ACTIVITY = 1
APPROVE_ACTIVITY = 2
REJECT_ACTIVITY = 3

class Report(models.Model):
	name = models.CharField(max_length=256)
	description = models.CharField(max_length=1024, blank=True)
	master_plan = models.ForeignKey('domain.MasterPlan')
	need_checkup = models.BooleanField(default=False) # Need to be sent to assistant to review
	need_approval = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('domain.UserAccount')

class ReportProject(models.Model):
	report = models.ForeignKey('Report')
	project = models.ForeignKey('domain.Project')

class ReportSchedule(models.Model):
	report_project = models.ForeignKey('ReportProject')
	due_date = models.DateField()
	is_submitted = models.BooleanField(default=False)
	last_submitted = models.DateTimeField(null=True)
	last_activity = models.IntegerField(default=SUBMIT_ACTIVITY)

class ReportScheduleActivity(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	activity = models.IntegerField()
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('domain.UserAccount')

class ReportScheduleFileResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	filename = models.CharField(max_length=512)
	uploaded = models.DateTimeField(auto_now_add=True)
	uploaded_by = models.ForeignKey('domain.UserAccount')
