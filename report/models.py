from django.contrib.auth.models import User
from django.db import models

class Report(models.Model):
	name = models.CharField(max_length=256)
	description = models.CharField(max_length=1024, blank=True)
	has_schedule = models.BooleanField(default=False)
	created = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('domain.UserAccount')

class ReportProject(models.Model):
	report = models.ForeignKey('Report')
	project = models.ForeignKey('domain.Project')

class ReportSchedule(models.Model):
	report_project = models.ForeignKey('ReportProject')
	due_date = models.DateField()
	is_submitted = models.BooleanField(default=False)
	submitted = models.DateTimeField(null=True)

class ReportScheduleFileResponse(models.Model):
	schedule = models.ForeignKey('ReportSchedule')
	filename = models.CharField(max_length=512)
	uploaded = models.DateTimeField(auto_now_add=True)
	uploaded_by = models.ForeignKey('domain.UserAccount')

