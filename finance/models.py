from django.db import models

class ProjectBudgetSchedule(models.Model):
	project = models.ForeignKey('domain.Project')
	target = models.IntegerField()
	result = models.IntegerField(default=0)
	target_on = models.DateField()
	claimed_on = models.DateField(null=True)
	remark = models.CharField(max_length=1000, blank=True)

class ProjectBudgetScheduleRevision(models.Model):
	schedule = models.ForeignKey('ProjectBudgetSchedule')
	org_target = models.IntegerField()
	org_result = models.IntegerField()
	org_target_on = models.DateField()
	
	new_target = models.IntegerField()
	new_result = models.IntegerField()
	new_target_on = models.DateField()
	
	revised_on = models.DateTimeField(auto_now=True)
	revised_by = models.ForeignKey('accounts.UserAccount')
