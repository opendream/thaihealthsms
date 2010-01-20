from django.contrib.auth.models import User
from django.db import models

SUBMIT_ACTIVITY = 1
APPROVE_ACTIVITY = 2
REJECT_ACTIVITY = 3

class ReportType(models.Model):
	name = models.CharField(max_length=256)
	sector = models.ForeignKey('domain.Sector', null=True)

class Report(models.Model):
	name = models.CharField(max_length=500)
	type = models.ForeignKey('ReportType', null=True)
	sector = models.ForeignKey('domain.Sector', null=True)
	need_checkup = models.BooleanField(default=False) # Need to be sent to sector manager assistant to review
	need_approval = models.BooleanField(default=False) # Need approval from sector manager assistant
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('domain.UserAccount')

class ReportProject(models.Model):
	report = models.ForeignKey('Report')
	project = models.ForeignKey('domain.Project')

class ReportSchedule(models.Model):
	report_project = models.ForeignKey('ReportProject')
	due_date = models.DateField(null=True)
	is_submitted = models.BooleanField(default=False)
	last_submitted = models.DateTimeField(null=True)
	last_activity = models.IntegerField(default=SUBMIT_ACTIVITY)

class ReportScheduleActivity(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	activity = models.IntegerField()
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('domain.UserAccount')

class ReportScheduleTextResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	text = models.CharField(max_length=512)
	submitted = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey('domain.UserAccount')

class ReportScheduleFileResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	filename = models.CharField(max_length=512)
	uploaded = models.DateTimeField(auto_now_add=True)
	uploaded_by = models.ForeignKey('domain.UserAccount')
