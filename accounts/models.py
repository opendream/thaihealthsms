from django.contrib.auth.models import User, Group
from django.db import models

class UserAccount(models.Model):
	user = models.ForeignKey(User, unique=True)
	sector = models.ForeignKey('domain.Sector', null=True)
	first_name = models.CharField(max_length=300, null=True)
	last_name = models.CharField(max_length=300, null=True)
	random_password = models.CharField(max_length=30, null=True)

class UserRoleResponsibility(models.Model):
	user = models.ForeignKey('UserAccount')
	role = models.ForeignKey(Group)
	sectors = models.ManyToManyField('domain.Sector', null=True)
	master_plans = models.ManyToManyField('domain.MasterPlan', null=True)
	plans = models.ManyToManyField('domain.Plan', null=True)
	projects = models.ManyToManyField('domain.Project', null=True)
	activities = models.ManyToManyField('domain.Activity', null=True)

class GroupName(models.Model):
	group = models.ForeignKey(Group, unique=True)
	name = models.CharField(max_length=512)
