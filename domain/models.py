from django.contrib.auth.models import User, Group
from django.db import models

#
# User, Role and Responsibility
#
class UserAccount(models.Model):
	user = models.ForeignKey(User, unique=True)
	sector = models.ForeignKey('Sector', null=True)
	first_name = models.CharField(max_length=300, null=True)
	last_name = models.CharField(max_length=300, null=True)

class UserRoleResponsibility(models.Model):
	user = models.ForeignKey(UserAccount)
	role = models.ForeignKey(Group)
	sectors = models.ManyToManyField('Sector', null=True)
	master_plans = models.ManyToManyField('MasterPlan', null=True)
	plans = models.ManyToManyField('Plan', null=True)
	projects = models.ManyToManyField('Project', null=True)
	activities = models.ManyToManyField('Activity', null=True)

#
# Organization
#
class Sector(models.Model):
	ref_no = models.IntegerField()
	name = models.CharField(max_length=512)

class MasterPlan(models.Model):
	sector = models.ForeignKey('Sector')
	ref_no = models.IntegerField()
	name = models.CharField(max_length=512)
	is_active = models.BooleanField(default=True)
	start_year = models.IntegerField() # Master plan for ThaiHealth has 3 years-span
	end_year = models.IntegerField()

class MasterPlanYear(models.Model):
	master_plan = models.ForeignKey('MasterPlan')
	year = models.IntegerField()
	start_month = models.DateField()
	end_month = models.DateField()

class Plan(models.Model):
	master_plan = models.ForeignKey('MasterPlan')
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)

class Project(models.Model): # Program, Project
	
	"""
	- [sector] and [master_plan] always have a valid value
	- [plan] is present, [parent_project] is not --> Project object is a PROGRAM or PROJECT that reported directly under a PLAN
	- [plan] is not present, [parent_project] is present --> Project object is a PROJECT that is under a PROGRAM
	- [plan] is not present, [parent_project] is not present too --> Project object is a PROGRAM that reported directly under MASTER PLAN, without any PLAN
	- [type] is to determine whether a Project object should be called a PROGRAM or PROJECT, it has no affect on organization hierarchy
	"""
	
	sector = models.ForeignKey('Sector')
	master_plan = models.ForeignKey('MasterPlan')
	plan = models.ForeignKey('Plan', null=True)
	parent_project = models.ForeignKey('self', null=True)
	
	prefix_name = models.IntegerField(default=0)
	PROJECT_IS_PROGRAM = 1
	PROJECT_IS_PROJECT = 2
	PROJECT_IS_SUB_PROJECT = 3
	
	ref_no = models.CharField(max_length=64, null=True)
	name = models.CharField(max_length=512)
	description = models.TextField(null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	status = models.IntegerField(default=0) # Not use yet

class Activity(models.Model):
	project = models.ForeignKey('Project')
	name = models.CharField(max_length=512)
	description = models.TextField(null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	status = models.IntegerField(default=0)

