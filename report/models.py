from django.contrib.auth.models import User
from django.db import models

NO_ACTIVITY = 0
SUBMIT_ACTIVITY = 1
APPROVE_ACTIVITY = 2
REJECT_ACTIVITY = 3
CANCEL_ACTIVITY = 4

class Report(models.Model):
	name = models.CharField(max_length=500)
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
	submitted_on = models.DateTimeField(null=True)
	state = models.IntegerField(default=NO_ACTIVITY)
	approval_on = models.DateTimeField(null=True)

class ReportScheduleTextResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule', primary_key=True)
	text = models.CharField(max_length=512)
	submitted = models.DateTimeField(auto_now_add=True)
	submitted_by = models.ForeignKey('domain.UserAccount')

class ReportScheduleFileResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	filename = models.CharField(max_length=512)
	uploaded = models.DateTimeField(auto_now_add=True)
	uploaded_by = models.ForeignKey('domain.UserAccount')
