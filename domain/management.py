# -*- encoding: utf-8 -*-

# Signal after syncdb
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission

from domain.models import *
from report.models import *

import calendar
import random

def after_syncdb(sender, **kwargs):

	"""
	THIS IS REAL PRODUCTION CODE
	"""
	
	# Sector ##################
	sector1, created = Sector.objects.get_or_create(ref_no='1', name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงหลัก')
	sector2, created = Sector.objects.get_or_create(ref_no='2', name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงรอง')
	sector3, created = Sector.objects.get_or_create(ref_no='3', name='สำนักสนับสนุนการสร้างสุขภาวะในพื้นที่ชุมชน')
	sector4, created = Sector.objects.get_or_create(ref_no='4', name='สำนักสนับสนุนการเรียนรู้และสุขภาวะองค์กร')
	sector5, created = Sector.objects.get_or_create(ref_no='5', name='สำนักรณรงค์สื่อสารสาธารณะและสังคม')
	sector6, created = Sector.objects.get_or_create(ref_no='6', name='สำนักสนับสนุนโครงการเปิดรับทั่วไป')
	sector7, created = Sector.objects.get_or_create(ref_no='7', name='สำนักสนับสนุนการพัฒนาระบบสุขภาพและบริการสุขภาพ')
	
	# User Roles ##################
	sector_manager_role, created = Group.objects.get_or_create(name='sector_manager')
	sector_manager_assistant_role, created = Group.objects.get_or_create(name='sector_manager_assistant')
	
	master_plan_manager_role, created = Group.objects.get_or_create(name='master_plan_manager')
	master_plan_manager_assistant_role, created = Group.objects.get_or_create(name='master_plan_manager_assistant')
	
	plan_manager_role, created = Group.objects.get_or_create(name='plan_manager')
	plan_manager_assistant_role, created = Group.objects.get_or_create(name='plan_manager_assistant')
	
	program_manager_role, created = Group.objects.get_or_create(name='program_manager')
	program_manager_assistant_role, created = Group.objects.get_or_create(name='program_manager_assistant')
	
	project_manager_role, created = Group.objects.get_or_create(name='project_manager')
	project_manager_assistant_role, created = Group.objects.get_or_create(name='project_manager_assistant')
	
	activity_manager_role, created = Group.objects.get_or_create(name='activity_manager')
	project_manager_assistant_role, created = Group.objects.get_or_create(name='project_manager_assistant')
	
	# Permission ##################
	# Permission.objects.get_or_create(name='', content_type='', codename='')
	
	
	# Administrator ##################
	admins = settings.ADMINS
	
	from django.core.mail import send_mail
	
	for admin in admins:
		try:
			User.objects.get(username=admin[0])
			
		except User.DoesNotExist:
			random_password = User.objects.make_random_password()
			admin_user = User.objects.create_user(admin[0], admin[1], random_password)
			admin_user.is_superuser = True
			admin_user.is_staff = True
			admin_user.save()
			
			email_content = 'Username: %s\nPassword: %s\n' % (admin[0], random_password)
			send_mail('Your account for Strategy Management Systems', email_content, settings.SYSTEM_NOREPLY_EMAIL, [admin[1]])
			
			admin_account = admin_user.get_profile()
			admin_account.first_name = "Administration"
			admin_account.last_name = ""
			admin_account.save()
	
	
	"""
	END HERE
	"""
	
	"""
	BELOW CODE IS FOR PROTOTYPE-PURPOSE ONLY
	"""
	
	if not Plan.objects.all():
		
		# Users ##################
		
		# Sector Managers
		sector_manager1 = User.objects.create_user("sector1", "sector1@example.com", "password")
		sector_manager1.groups.add(sector_manager_role)
		
		sector_manager_account1 = sector_manager1.get_profile()
		sector_manager_account1.sector = sector7
		sector_manager_account1.first_name = "Sector"
		sector_manager_account1.last_name = "Manager"
		sector_manager_account1.save()
		
		user_responsibility = UserRoleResponsibility.objects.create(user=sector_manager_account1, role=sector_manager_role)
		user_responsibility.sectors.add(sector7)
		
		# User - Assistants
		sector_manager_assistant1 = User.objects.create_user("pakchuda", "assistant1@example.com", "password")
		sector_manager_assistant1.groups.add(sector_manager_assistant_role)
		
		sector_manager_assistant_account1 = sector_manager_assistant1.get_profile()
		sector_manager_assistant_account1.sector = sector7
		sector_manager_assistant_account1.first_name = "Sector"
		sector_manager_assistant_account1.last_name = "Assistant"
		sector_manager_assistant_account1.save()
				
		# Program Managers
		program_manager1 = User.objects.create_user("program1", "program1@example.com", "password")
		program_manager1.groups.add(program_manager_role)
		
		program_manager2 = User.objects.create_user("program2", "program2@example.com", "password")
		program_manager2.groups.add(program_manager_role)
		
		program_manager3 = User.objects.create_user("program3", "program3@example.com", "password")
		program_manager3.groups.add(program_manager_role)
		
		program_manager_account1 = program_manager1.get_profile()
		program_manager_account1.sector = sector7
		program_manager_account1.first_name = "Program1"
		program_manager_account1.last_name = "Manager"
		program_manager_account1.save()
		
		program_manager_account2 = program_manager2.get_profile()
		program_manager_account2.sector = sector7
		program_manager_account2.first_name = "Program2"
		program_manager_account2.last_name = "Manager"
		program_manager_account2.save()
		
		program_manager_account3 = program_manager3.get_profile()
		program_manager_account3.sector = sector7
		program_manager_account3.first_name = "Program3"
		program_manager_account3.last_name = "Manager"
		program_manager_account3.save()
		
		# Program Manager Assistants
		program_manager_assistant1 = User.objects.create_user("program_assistant1", "program_assistant1@example.com", "password")
		program_manager_assistant1.groups.add(program_manager_assistant_role)
		
		program_manager_assistant_account1 = program_manager1.get_profile()
		program_manager_assistant_account1.sector = sector7
		program_manager_assistant_account1.first_name = "Program1"
		program_manager_assistant_account1.last_name = "Assistant"
		program_manager_assistant_account1.save()
		
		program_manager_assistant2 = User.objects.create_user("program_assistant2", "program_assistant2@example.com", "password")
		program_manager_assistant2.groups.add(program_manager_assistant_role)
		
		program_manager_assistant_account2 = program_manager1.get_profile()
		program_manager_assistant_account2.sector = sector7
		program_manager_assistant_account2.first_name = "Program2"
		program_manager_assistant_account2.last_name = "Assistant"
		program_manager_assistant_account2.save()
		
		# Project Managers
		project_manager1 = User.objects.create_user("project1", "project1@example.com", "password")
		project_manager1.groups.add(project_manager_role)
		
		project_manager2 = User.objects.create_user("project2", "project2@example.com", "password")
		project_manager2.groups.add(project_manager_role)
		
		project_manager_account1 = project_manager1.get_profile()
		project_manager_account1.sector = sector7
		project_manager_account1.first_name = "Project1"
		project_manager_account1.last_name = "Manager"
		project_manager_account1.save()
		
		project_manager_account2 = project_manager2.get_profile()
		project_manager_account2.sector = sector7
		project_manager_account2.first_name = "Project2"
		project_manager_account2.last_name = "Manager"
		project_manager_account2.save()
		
		# Project Manager Assistants
		project_manager_assistant1 = User.objects.create_user("project_assistant1", "project_assistant1@example.com", "password")
		project_manager_assistant1.groups.add(project_manager_assistant_role)
		
		project_manager_assistant2 = User.objects.create_user("project_assistant2", "project_assistant2@example.com", "password")
		project_manager_assistant2.groups.add(project_manager_assistant_role)
		
		project_manager_assistant_account1 = project_manager_assistant1.get_profile()
		project_manager_assistant_account1.sector = sector7
		project_manager_assistant_account1.first_name = "Project1"
		project_manager_assistant_account1.last_name = "Assistant"
		project_manager_assistant_account1.save()
		
		project_manager_assistant_account2 = project_manager_assistant2.get_profile()
		project_manager_assistant_account2.sector = sector7
		project_manager_assistant_account2.first_name = "Project2"
		project_manager_assistant_account2.last_name = "Assistant"
		project_manager_assistant_account2.save()
		
		# Master Plan ##################
		master_plan12 = MasterPlan.objects.create(sector=sector7, ref_no="12", name="แผนสนับสนุนการสร้างเสริมสุขภาพผ่านระบบบริการสุขภาพ", start_year=2009, end_year=2011)
		master_plan13 = MasterPlan.objects.create(sector=sector7, ref_no="13", name="แผนพัฒนาระบบและกลไกสนับสนุนเพื่อการสร้างเสริมสุขภาพ", start_year=2009, end_year=2011)
		
		# Plan ##################
		plan1204 = Plan.objects.create(master_plan=master_plan12, ref_no="1201", name="กลุ่มแผนงานที่หนึ่ง")
		plan1201 = Plan.objects.create(master_plan=master_plan12, ref_no="1202", name="กลุ่มแผนงานที่สอง")
		plan1202 = Plan.objects.create(master_plan=master_plan12, ref_no="1203", name="กลุ่มแผนงานที่สาม")
		plan1203 = Plan.objects.create(master_plan=master_plan12, ref_no="1204", name="กลุ่มแผนงานที่สี่")
		
		plan1301 = Plan.objects.create(master_plan=master_plan13, ref_no="1301", name="กลุ่มแผนงานที่ห้า")
		plan1302 = Plan.objects.create(master_plan=master_plan13, ref_no="1302", name="กลุ่มแผนงานที่หก")
		
		# Program ##################
		program1201_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00001", name="แผนงานที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1201_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00002", name="แผนงานที่สอง", start_date=date(2009,12,16), end_date=date(2011,12,15))
		program1201_3 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00003", name="แผนงานที่สาม", start_date=date(2008,12,16), end_date=date(2009,12,15))
		program1201_4 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00004", name="แผนงานที่สี่", start_date=date(2008,12,16), end_date=date(2009,12,15))
		program1201_5 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00005", name="แผนงานที่ห้า", start_date=date(2010,12,16), end_date=date(2011,12,15))
		
		program1202_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00001", name="แผนงานที่หก", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1202_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00002", name="แผนงานที่เจ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1203_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00001", name="แผนงานที่แปด", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1203_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00002", name="แผนงานที่เก้า", start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1204_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00001", name="แผนงานที่สิบ", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1204_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00002", name="แผนงานที่สิบเอ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1301_1 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1301, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="31-00001", name="แผนงานที่สิบสอง", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1301_2 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1301, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="31-00002", name="แผนงานที่สิบสาม", start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1302_1 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1302, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="32-00001", name="แผนงานที่สิบสี่", start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1302_2 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1302, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="32-00002", name="แผนงานที่สิบห้า", start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		user_responsibility = UserRoleResponsibility.objects.create(user=program_manager_account1, role=program_manager_role)
		user_responsibility.projects.add(program1201_1)
		user_responsibility.projects.add(program1201_3)
		user_responsibility.projects.add(program1202_1)
		user_responsibility.projects.add(program1202_2)
		user_responsibility.projects.add(program1204_1)
		user_responsibility.projects.add(program1204_2)
		
		user_responsibility = UserRoleResponsibility.objects.create(user=program_manager_account2, role=program_manager_role)
		user_responsibility.projects.add(program1201_2)
		user_responsibility.projects.add(program1201_4)
		user_responsibility.projects.add(program1201_5)
		user_responsibility.projects.add(program1203_1)
		user_responsibility.projects.add(program1203_2)
		
		user_responsibility = UserRoleResponsibility.objects.create(user=program_manager_account3, role=program_manager_role)
		user_responsibility.projects.add(program1301_1)
		user_responsibility.projects.add(program1301_2)
		user_responsibility.projects.add(program1302_1)
		user_responsibility.projects.add(program1302_2)
		
		# Project ##################
		project1201_1_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-001", name="โครงการทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,4,1))
		project1201_1_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-002", name="โครงการทดลองทีสอง", start_date=date(2009,4,1), end_date=date(2009,8,1))
		project1201_1_003 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-003", name="โครงการทดลองที่สาม", start_date=date(2009,8,1), end_date=date(2009,12,1))
		project1201_1_004 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-004", name="โครงการทดลองที่สี่", start_date=date(2009,12,1), end_date=date(2010,4,1))
		project1201_1_005 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-005", name="โครงการทดลองที่ห้า", start_date=date(2010,4,1), end_date=date(2010,8,1))
		project1201_1_006 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-006", name="โครงการทดลองที่หก", start_date=date(2010,8,1), end_date=date(2010,12,1))
		
		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_account1, role=project_manager_role)
		user_responsibility.projects.add(project1201_1_001)
		user_responsibility.projects.add(project1201_1_002)
		user_responsibility.projects.add(project1201_1_003)
		
		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_account1, role=project_manager_role)
		user_responsibility.projects.add(project1201_1_004)
		user_responsibility.projects.add(project1201_1_005)
		user_responsibility.projects.add(project1201_1_006)
		
		# Assistant Responsibility
		user_responsibility = UserRoleResponsibility.objects.create(user=sector_manager_assistant_account1, role=sector_manager_assistant_role)
		user_responsibility.projects.add(program1201_1)
		user_responsibility.projects.add(program1201_2)
		user_responsibility.projects.add(program1201_3)
		
		# Activity ##################
		activity1 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,3,15))
		activity2 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สอง", start_date=date(2009,3,1), end_date=date(2009,3,16))
		activity3 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สาม", start_date=date(2009,11,16), end_date=date(2009,12,1))
		activity4 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สี่", start_date=date(2010,6,15), end_date=date(2010, 6,16))
		activity5 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่ห้า", start_date=date(2011,6,14), end_date=date(2011,8,16))
		
	"""
	END HERE
	"""
	
	
	
	"""
	# Report
	report1 = Report.objects.create(name="รายงานความก้าวหน้าประจำเดือน", created_by=assistant_account1)
	report2 = Report.objects.create(name="รายงานการเงินประจำเดือน", created_by=assistant_account1)
	
	report_program11 = ReportProject.objects.create(report=report1, project=program1204_1)
	report_program12 = ReportProject.objects.create(report=report2, project=program1204_1)

	report_project11 = ReportProject.objects.create(report=report1, project=project1204_1_001)
	report_project12 = ReportProject.objects.create(report=report1, project=project1204_1_002)
	report_project21 = ReportProject.objects.create(report=report2, project=project1204_1_001)
	report_project22 = ReportProject.objects.create(report=report2, project=project1204_1_002)
	
	
	# Schedule for Program
	ReportSchedule.objects.create(report_project=report_program11, due_date=date(2010, 02, 15))
	ReportSchedule.objects.create(report_project=report_program11, due_date=date(2010, 01, 15))
	ReportSchedule.objects.create(report_project=report_program11, due_date=date(2009, 12, 15), is_submitted=True, last_submitted=datetime.now())
	
	ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 02, 15))
	ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 01, 15), is_submitted=True, last_submitted=datetime.now())
	ReportSchedule.objects.create(report_project=report_program12, due_date=date(2009, 12, 15), is_submitted=True, last_submitted=datetime.now())
	
	# Schedule for Project
	ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 12, 15), is_submitted=True, last_submitted=datetime.now())
	ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 11, 15), is_submitted=True, last_submitted=datetime.now())
	ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 10, 15), is_submitted=True, last_submitted=datetime.now())
	
	ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 12, 15), is_submitted=True, last_submitted=datetime.now())
	ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 11, 15), is_submitted=True, last_submitted=datetime.now())
	ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 12, 15), is_submitted=True, last_submitted=datetime.now())
	
	ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  3, 15))
	ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  2, 15))
	ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  1, 15))
	
	ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  3, 15))
	ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  2, 15))
	ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  1, 15), is_submitted=True, last_submitted=datetime.now())

	# KPI
	
	# Operation KPI
	op_kpi1 = MasterPlanKPI.objects.create(ref_no="R1", name="เกิดพื้นที่การเรียนรู้", category=MasterPlanKPI.OPERATION_CATEGORY, master_plan=master_plan12)
	op_kpi2 = MasterPlanKPI.objects.create(ref_no="R2", name="เกิดข้อเสนอเชิงนโยบาย", category=MasterPlanKPI.OPERATION_CATEGORY, master_plan=master_plan12)
	op_kpi3 = MasterPlanKPI.objects.create(ref_no="R3", name="เกิดผู้นำการเปลี่ยนแปลง", category=MasterPlanKPI.OPERATION_CATEGORY, master_plan=master_plan12)
	
	# Teamwork KPI
	team_kpi1 = MasterPlanKPI.objects.create(ref_no="", name="ความสามารถในการทำงานร่วมกัน", category=MasterPlanKPI.TEAMWORK_CATEGORY, master_plan=master_plan12)
	team_kpi2 = MasterPlanKPI.objects.create(ref_no="", name="การสื่อสารระหว่างทีม", category=MasterPlanKPI.TEAMWORK_CATEGORY, master_plan=master_plan12)
	
	# Partner
	partner_kpi1 = MasterPlanKPI.objects.create(ref_no="", name="ความร่วมมือ", category=MasterPlanKPI.PARTNER_CATEGORY, master_plan=master_plan12)
	partner_kpi2 = MasterPlanKPI.objects.create(ref_no="", name="การสื่อสาร", category=MasterPlanKPI.PARTNER_CATEGORY, master_plan=master_plan12)
	
	op_target1 = KPITargetProject.objects.create(kpi=op_kpi1, project=program1204_1)
	op_target2 = KPITargetProject.objects.create(kpi=op_kpi2, project=program1204_1)
	op_target3 = KPITargetProject.objects.create(kpi=op_kpi3, project=program1204_1)
	
	op_target4 = KPITargetProject.objects.create(kpi=op_kpi1, project=program1201_1)
	op_target5 = KPITargetProject.objects.create(kpi=op_kpi1, project=program1201_1)
	op_target6 = KPITargetProject.objects.create(kpi=op_kpi1, project=program1201_1)
	
	team_target1 = KPITargetProject.objects.create(kpi=team_kpi1, project=program1204_1)
	team_target2 = KPITargetProject.objects.create(kpi=team_kpi2, project=program1204_1)
	
	partner_target1 = KPITargetProject.objects.create(kpi=partner_kpi1, project=program1204_1)
	partner_target2 = KPITargetProject.objects.create(kpi=partner_kpi2, project=program1204_1)
	
	submission1  = KPISubmission.objects.create(target=op_target1, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	submission2  = KPISubmission.objects.create(target=op_target1, target_score=100, result_score=100, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission3  = KPISubmission.objects.create(target=op_target1, target_score=100, result_score= 50, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	submission4  = KPISubmission.objects.create(target=op_target1, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	submission5  = KPISubmission.objects.create(target=op_target2, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	submission6  = KPISubmission.objects.create(target=op_target2, target_score=100, result_score= 90, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission7  = KPISubmission.objects.create(target=op_target2, target_score=100, result_score= 40, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	submission8  = KPISubmission.objects.create(target=op_target2, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	submission9  = KPISubmission.objects.create(target=op_target3, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	submission10 = KPISubmission.objects.create(target=op_target3, target_score=100, result_score=120, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission11 = KPISubmission.objects.create(target=op_target3, target_score=100, result_score= 80, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	submission12 = KPISubmission.objects.create(target=op_target3, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	KPISubmission.objects.create(target=op_target4, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	KPISubmission.objects.create(target=op_target4, target_score=100, result_score=100, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	KPISubmission.objects.create(target=op_target4, target_score=100, result_score= 50, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	KPISubmission.objects.create(target=op_target4, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	KPISubmission.objects.create(target=op_target5, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	KPISubmission.objects.create(target=op_target5, target_score=100, result_score= 90, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	KPISubmission.objects.create(target=op_target5, target_score=100, result_score= 40, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	KPISubmission.objects.create(target=op_target5, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	KPISubmission.objects.create(target=op_target6, target_score=100, result_score=100, start_date=date(2009,  7,  1), end_date=date(2009,  9,  1))
	KPISubmission.objects.create(target=op_target6, target_score=100, result_score=120, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	KPISubmission.objects.create(target=op_target6, target_score=100, result_score= 80, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	KPISubmission.objects.create(target=op_target6, target_score=100, result_score=  0, start_date=date(2010,  4,  1), end_date=date(2010,  6,  1))
	
	
	submission13 = KPISubmission.objects.create(target=team_target1, target_score=100, result_score=100, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission14 = KPISubmission.objects.create(target=team_target1, target_score=100, result_score=60, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	submission15 = KPISubmission.objects.create(target=team_target2, target_score=100, result_score=100, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission16 = KPISubmission.objects.create(target=team_target2, target_score=100, result_score=30, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	
	
	
	submission17 = KPISubmission.objects.create(target=partner_target1, target_score=100, result_score=60, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission18 = KPISubmission.objects.create(target=partner_target1, target_score=100, result_score=10, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	submission19 = KPISubmission.objects.create(target=partner_target2, target_score=100, result_score=100, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	submission20 = KPISubmission.objects.create(target=partner_target2, target_score=100, result_score=40, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	
	KPISubmissionRevision.objects.create(submission=submission2, target_score=100, result_score=20, submitted_by=program_manager_account1)
	KPISubmissionRevision.objects.create(submission=submission2, target_score=100, result_score=60, submitted_by=program_manager_account1)
	
	KPISubmissionRevision.objects.create(submission=submission3, target_score=100, result_score=10, submitted_by=program_manager_account1)
	
	KPISubmissionRevision.objects.create(submission=submission5, target_score=100, result_score=10, submitted_by=program_manager_account1)
	KPISubmissionRevision.objects.create(submission=submission5, target_score=100, result_score=30, submitted_by=program_manager_account1)
	KPISubmissionRevision.objects.create(submission=submission5, target_score=100, result_score=60, submitted_by=program_manager_account1)
	
	finance_submission1 = FinanceKPISubmission.objects.create(project=program1204_1, budget=1000000, spent_budget=900000, start_date=date(2009, 10,  1), end_date=date(2009, 12,  1))
	finance_submission2 = FinanceKPISubmission.objects.create(project=program1204_1, budget=1000000, spent_budget=200000, start_date=date(2010,  1,  1), end_date=date(2010,  3,  1))
	
	FinanceKPISubmissionRevision.objects.create(submission=finance_submission1, budget=1000000, spent_budget=100000, submitted_by=program_manager_account1)
	FinanceKPISubmissionRevision.objects.create(submission=finance_submission1, budget=1000000, spent_budget=300000, submitted_by=program_manager_account1)
	FinanceKPISubmissionRevision.objects.create(submission=finance_submission1, budget=1000000, spent_budget=700000, submitted_by=program_manager_account1)
	
	FinanceKPISubmissionRevision.objects.create(submission=finance_submission2, budget=1000000, spent_budget=100000, submitted_by=program_manager_account1)
	"""


from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="domain.management")