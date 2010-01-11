from django.contrib.auth.models import User
from django.db import models

class GlobalSettings(models.Model):
	working_annual = models.IntegerField()

#
# User and Role
#
class UserAccount(models.Model):
	user = models.ForeignKey(User, unique=True)
	role = models.CharField(max_length=64, null=True) # assistant, program_manager, project_manager
	sector = models.ForeignKey('Sector', related_name="user_sector", null=True)
	first_name = models.CharField(max_length=300, null=True)
	last_name = models.CharField(max_length=300, null=True)
	projects = models.ManyToManyField('Project')

#
# Organization
#
class Sector(models.Model):
	ref_no = models.CharField(max_length=64, unique=True)
	name = models.CharField(max_length=512)
	manager = models.ForeignKey('UserAccount', null=True, related_name="sector_manager")

class MasterPlan(models.Model):
	sector = models.ForeignKey('Sector')
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	is_active = models.BooleanField(default=True)
	start_year = models.IntegerField() # Master plan for ThaiHealth has 3 years-span
	end_year = models.IntegerField()
	manager = models.ForeignKey('UserAccount', null=True)

class Plan(models.Model):
	master_plan = models.ForeignKey('MasterPlan')
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	manager = models.ForeignKey('UserAccount', null=True)

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
	
	type = models.IntegerField(default=0)
	PROGRAM_TYPE = 1
	PROJECT_TYPE = 2
	
	ref_no = models.CharField(max_length=64, null=True)
	name = models.CharField(max_length=512)
	description = models.TextField(null=True)
	start_date = models.DateField()
	end_date = models.DateField()
	status = models.IntegerField(default=0) # Not use yet
	manager = models.ForeignKey('UserAccount', null=True)
	budget = models.IntegerField(default=0)
	
class Activity(models.Model):
	project = models.ForeignKey('Project')
	name = models.CharField(max_length=512)
	description = models.TextField(null=True)
	start_date = models.DateField()
	end_date = models.DateField()
	status = models.IntegerField(default=0)
	manager = models.ForeignKey('UserAccount', null=True)
	
	location = models.CharField(max_length=512)
	result_goal = models.TextField()
	result_real = models.TextField()

#
# KPI
#
class KPI(models.Model):
	ref_no = models.CharField(max_length=64)
	name = models.CharField(max_length=512)
	category = models.IntegerField() # Finance, Operation, Teamwork, Partner
	full_score = models.IntegerField()
	unit_type = models.IntegerField(default=0) # quantitative, expectation etc.
	unit_name = models.CharField(max_length=256)

class ProjectKPI(models.Model):
	kpi = models.ForeignKey('KPI')
	project = models.ForeignKey('Project')
	expect_date = models.DateField()
	expect_score = models.IntegerField()
	score = models.IntegerField()




#
# Finance
#	
class ProjectBudgetSchedule(models.Model):
	project = models.ForeignKey('Project')
	scheduled_on = models.DateField()
	expected_budget = models.IntegerField(default=0)
	used_budget = models.IntegerField(default=0)



