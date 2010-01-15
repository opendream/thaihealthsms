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
	ref_no = models.CharField(max_length=64, unique=True)
	name = models.CharField(max_length=512)

class MasterPlan(models.Model):
	sector = models.ForeignKey('Sector')
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	is_active = models.BooleanField(default=True)
	start_year = models.IntegerField() # Master plan for ThaiHealth has 3 years-span
	end_year = models.IntegerField()

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
	
	budget = models.IntegerField(default=0)
	
class Activity(models.Model):
	project = models.ForeignKey('Project')
	name = models.CharField(max_length=512)
	description = models.TextField(null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	status = models.IntegerField(default=0)

	location = models.CharField(max_length=512)
	result_goal = models.TextField()
	result_real = models.TextField()

#
# Project Finance
#
class ProjectBudgetSchedule(models.Model):
	project = models.ForeignKey('Project')
	expected_budget = models.IntegerField()
	used_budget = models.IntegerField()
	year = models.IntegerField() # Buddhist calendar (e.g. use 2552 to represent 2008 A.D. in Gregorian calendar)
	scheduled_on = models.DateField()
	requested_on = models.DateField()

class ProjectBudgetScheduleRevision(models.Model):
	schedule = models.ForeignKey('ProjectBudgetSchedule')
	expected_budget = models.IntegerField()
	used_budget = models.IntegerField()
	revised_on = models.DateTimeField(auto_now=True)
	revised_by = models.ForeignKey('UserAccount')

#
# KPI
#
class MasterPlanKPI(models.Model):
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	category = models.IntegerField() # Operation, Teamwork, Partner
	master_plan = models.ForeignKey('MasterPlan')
	created_on = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey('UserAccount')
	
	OPERATION_CATEGORY = 1
	TEAMWORK_CATEGORY = 2
	PARTNER_CATEGORY = 3

class KPISchedule(models.Model):
	kpi = models.ForeignKey('MasterPlanKPI')
	project = models.ForeignKey('Project')
	year = models.IntegerField() # Gregorian calendar e.g. 2009 -- Fill when create KPI
	target_score = models.IntegerField()
	result_score = models.IntegerField()
	start_date = models.DateField()
	end_date = models.DateField()
	last_update = models.DateTimeField(auto_now=True)
	
class KPIScheduleRevision(models.Model):
	schedule = models.ForeignKey('KPISchedule')
	target_score = models.IntegerField()
	result_score = models.IntegerField()
	revised_on = models.DateTimeField(auto_now_add=True)
	revised_by = models.ForeignKey('UserAccount')


