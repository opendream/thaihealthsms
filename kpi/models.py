from django.db import models

class KPICategory(models.Model): # Operation, Teamwork, Partner, OPDC
	name = models.CharField(max_length=512)

class KPI(models.Model):
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	category = models.ForeignKey('KPICategory')
	unit_name = models.CharField(max_length=128)
	master_plan = models.ForeignKey('domain.MasterPlan', null=True) # If master_plan is None, this KPI will be used throughout organization
	is_visible_to_project = models.BooleanField(default=True)
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('accounts.UserAccount')

class KPISchedule(models.Model):
	kpi = models.ForeignKey('KPI')
	project = models.ForeignKey('domain.Project')
	target = models.IntegerField()
	result = models.IntegerField()
	target_on = models.DateField()
	remark = models.CharField(max_length=1000, blank=True)

class KPIScheduleRevision(models.Model):
	schedule = models.ForeignKey('KPISchedule')
	org_target = models.IntegerField()
	org_result = models.IntegerField()
	org_target_on = models.DateField()
	new_target = models.IntegerField()
	new_result = models.IntegerField()
	new_target_on = models.DateField()
	revised_on = models.DateTimeField(auto_now_add=True)
	revised_by = models.ForeignKey('accounts.UserAccount')
