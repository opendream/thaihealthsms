# -*- encoding: utf-8 -*-
from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.models import User

from domain.models import *
from report.models import *

import calendar
import random

def after_syncdb(sender, **kwargs):
	"""
	BELOW CODE IS FOR PROTOTYPE-PURPOSE ONLY
	"""
	
	if not UserAccount.objects.all(): # One thing to trigger them all
		# Sector
		sector1 = Sector.objects.create(ref_no="1", name="สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงหลัก")
		sector2 = Sector.objects.create(ref_no="2", name="สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงรอง")
		sector3 = Sector.objects.create(ref_no="3", name="สำนักสนับสนุนการสร้างสุขภาวะในพื้นที่ชุมชน")
		sector4 = Sector.objects.create(ref_no="4", name="สำนักสนับสนุนการเรียนรู้และสุขภาวะองค์กร")
		sector5 = Sector.objects.create(ref_no="5", name="สำนักรณรงค์สื่อสารสาธารณะและสังคม")
		sector6 = Sector.objects.create(ref_no="6", name="สำนักสนับสนุนโครงการเปิดรับทั่วไป")
		sector7 = Sector.objects.create(ref_no="7", name="สำนักสนับสนุนการพัฒนาระบบสุขภาพและบริการสุขภาพ")
		
		# Assistants
		assistant1 = User.objects.create_user("pakchuda", "assistant1@example.com", "password")
		
		assistant_account1 = assistant1.get_profile()
		assistant_account1.role = "assistant"
		assistant_account1.sector = sector7
		assistant_account1.first_name = "Pakchuda"
		assistant_account1.last_name = "Wasuwat"
		assistant_account1.save()
		
		# Sector Managers
		sector_manager1 = User.objects.create_user("sector1", "sector1@example.com", "password")
		
		sector_manager_account1 = sector_manager1.get_profile()
		sector_manager_account1.role = "sector_manager"
		sector_manager_account1.sector = sector7
		sector_manager_account1.first_name = "FirstName"
		sector_manager_account1.last_name = "LastName"
		sector_manager_account1.save()
		
		sector7.manager = sector_manager_account1
		sector7.save()
		
		# Program Managers
		program_manager1 = User.objects.create_user("program1", "pm11@example.com", "password")
		program_manager2 = User.objects.create_user("program2", "pm12@example.com", "password")
		
		program_manager_account1 = program_manager1.get_profile()
		program_manager_account1.role = "program_manager"
		program_manager_account1.sector = sector7
		program_manager_account1.first_name = "FirstName"
		program_manager_account1.last_name = "LastName"
		program_manager_account1.save()
		
		program_manager_account2 = program_manager2.get_profile()
		program_manager_account2.role = "program_manager"
		program_manager_account2.sector = sector7
		program_manager_account2.first_name = "FirstName"
		program_manager_account2.last_name = "LastName"
		program_manager_account2.save()
		
		# Project Managers
		project_manager1 = User.objects.create_user("project1", "pm21@example.com", "password")
		project_manager2 = User.objects.create_user("project2", "pm22@example.com", "password")
		project_manager3 = User.objects.create_user("project3", "pm23@example.com", "password")
		project_manager4 = User.objects.create_user("project4", "pm24@example.com", "password")
		
		project_manager_account1 = project_manager1.get_profile()
		project_manager_account1.role = "project_manager"
		project_manager_account1.sector = sector7
		project_manager_account1.first_name = "FirstName"
		project_manager_account1.last_name = "LastName"
		project_manager_account1.save()
		
		project_manager_account2 = project_manager2.get_profile()
		project_manager_account2.role = "project_manager"
		project_manager_account2.sector = sector7
		project_manager_account2.first_name = "FirstName"
		project_manager_account2.last_name = "LastName"
		project_manager_account2.save()
		
		project_manager_account3 = project_manager3.get_profile()
		project_manager_account3.role = "project_manager"
		project_manager_account3.sector = sector7
		project_manager_account3.first_name = "FirstName"
		project_manager_account3.last_name = "LastName"
		project_manager_account3.save()
		
		project_manager_account4 = project_manager4.get_profile()
		project_manager_account4.role = "project_manager"
		project_manager_account4.sector = sector7
		project_manager_account4.first_name = "FirstName"
		project_manager_account4.last_name = "LastName"
		project_manager_account4.save()
		
		# Master Plan
		master_plan12 = MasterPlan.objects.create(sector=sector7, ref_no="12", name="แผนสนับสนุนการสร้างเสริมสุขภาพผ่านระบบบริการสุขภาพ", start_year=2009, end_year=2011)
		master_plan13 = MasterPlan.objects.create(sector=sector7, ref_no="13", name="แผนพัฒนาระบบและกลไกสนับสนุนเพื่อการสร้างเสริมสุขภาพ", start_year=2009, end_year=2011)
		
		# Plan
		plan1201 = Plan.objects.create(master_plan=master_plan12, ref_no="1201", name="Plan 1201")
		plan1202 = Plan.objects.create(master_plan=master_plan12, ref_no="1202", name="Plan 1202")
		
		plan1301 = Plan.objects.create(master_plan=master_plan13, ref_no="1301", name="Plan 1301")
		plan1302 = Plan.objects.create(master_plan=master_plan13, ref_no="1302", name="Plan 1302")
		
		# Program
		program1201_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="1201-1", name="Program 1201-1", manager=program_manager_account1, start_date=date(2008, 1, 1), end_date=date(2011,12, 1))
		program1201_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="1201-2", name="Program 1201-2", manager=program_manager_account2, start_date=date(2009, 1, 1), end_date=date(2012,06, 1))
		program1201_3 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="1201-3", name="Program 1201-3", manager=program_manager_account1, start_date=date(2009, 1, 1), end_date=date(2009,12, 1))
		program1201_4 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="1201-4", name="Program 1201-4", manager=program_manager_account2, start_date=date(2010, 6, 1), end_date=date(2010,12, 1))
		
		program1202_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="1202-1", name="Program 1202-1", manager=program_manager_account1, start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1202_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="1202-2", name="Program 1202-2", manager=program_manager_account2, start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1301_1 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1301, type=Project.PROGRAM_TYPE, ref_no="1301-1", name="Program 1301-1", manager=program_manager_account1, start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1301_2 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1301, type=Project.PROGRAM_TYPE, ref_no="1301-2", name="Program 1302-2", manager=program_manager_account2, start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1302_1 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1302, type=Project.PROGRAM_TYPE, ref_no="1302-1", name="Program 1301-1", manager=program_manager_account1, start_date=date(2008,12,16), end_date=date(2011,12,15))
		program1302_2 = Project.objects.create(sector=sector7, master_plan=master_plan13, plan=plan1302, type=Project.PROGRAM_TYPE, ref_no="1302-2", name="Program 1302-2", manager=program_manager_account2, start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		# Project
		project1201_1_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, type=Project.PROJECT_TYPE, ref_no="1201-1-001", name="Project 1201-1-001", manager=project_manager_account1, start_date=date(2008, 1, 1), end_date=date(2009,12, 1))
		project1201_1_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_1, type=Project.PROJECT_TYPE, ref_no="1201-1-002", name="Project 1201-1-002", manager=project_manager_account2, start_date=date(2009, 1, 1), end_date=date(2011,12, 1))
		
		project1201_2_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_2, type=Project.PROJECT_TYPE, ref_no="1201-1-001", name="Project 1201-2-001", manager=project_manager_account1, start_date=date(2009, 1, 1), end_date=date(2010,12, 1))
		project1201_2_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_2, type=Project.PROJECT_TYPE, ref_no="1201-1-002", name="Project 1201-2-002", manager=project_manager_account2, start_date=date(2010, 1, 1), end_date=date(2012, 6, 1))
		
		project1201_3_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_3, type=Project.PROJECT_TYPE, ref_no="1201-1-001", name="Project 1201-3-001", manager=project_manager_account1, start_date=date(2009, 1, 1), end_date=date(2009, 6, 1))
		project1201_3_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_3, type=Project.PROJECT_TYPE, ref_no="1201-1-002", name="Project 1201-3-002", manager=project_manager_account2, start_date=date(2009, 6, 1), end_date=date(2011,12, 1))
		
		project1201_4_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_4, type=Project.PROJECT_TYPE, ref_no="1201-1-001", name="Project 1201-4-001", manager=project_manager_account1, start_date=date(2010, 6, 1), end_date=date(2010, 9, 1))
		project1201_4_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1201_4, type=Project.PROJECT_TYPE, ref_no="1201-1-002", name="Project 1201-4-002", manager=project_manager_account2, start_date=date(2010, 9, 1), end_date=date(2010,12, 1))
		
		# Assist Projects
		assistant_account1.projects.add(program1201_1)
		assistant_account1.projects.add(program1201_2)
		assistant_account1.projects.add(program1201_3)
		
		# Activity
		activity1 = Activity.objects.create(project=project1201_1_001, name="Activity 1", start_date=date(2008,12, 1), end_date=date(2009,12,16))
		activity2 = Activity.objects.create(project=project1201_1_001, name="Activity 2", start_date=date(2009,12, 1), end_date=date(2010,12,16))
		activity3 = Activity.objects.create(project=project1201_1_001, name="Activity 3", start_date=date(2010,12,16), end_date=date(2012,12,16))
		activity4 = Activity.objects.create(project=project1201_1_001, name="Activity 4", start_date=date(2009,12,15), end_date=date(2010, 6,16))
		activity5 = Activity.objects.create(project=project1201_1_001, name="Activity 5", start_date=date(2009,12,14), end_date=date(2010,12,16))
		
		
		# Report
		report1 = Report.objects.create(name="รายงานความก้าวหน้าประจำเดือน", created_by=assistant_account1)
		report2 = Report.objects.create(name="รายงานการเงินประจำเดือน", created_by=assistant_account1)
		
		report_program11 = ReportProject.objects.create(report=report1, project=program1201_1)
		report_program12 = ReportProject.objects.create(report=report1, project=program1201_2)
		report_program13 = ReportProject.objects.create(report=report1, project=program1201_3)
		report_program14 = ReportProject.objects.create(report=report1, project=program1201_4)
		report_program21 = ReportProject.objects.create(report=report2, project=program1201_1)
		report_program22 = ReportProject.objects.create(report=report2, project=program1201_2)
		report_program23 = ReportProject.objects.create(report=report2, project=program1201_3)
		report_program24 = ReportProject.objects.create(report=report2, project=program1201_4)
		
		report_project11 = ReportProject.objects.create(report=report1, project=project1201_1_001)
		report_project12 = ReportProject.objects.create(report=report1, project=project1201_1_002)
		report_project13 = ReportProject.objects.create(report=report1, project=project1201_2_001)
		report_project14 = ReportProject.objects.create(report=report1, project=project1201_2_002)
		report_project15 = ReportProject.objects.create(report=report1, project=project1201_3_001)
		report_project16 = ReportProject.objects.create(report=report1, project=project1201_3_002)
		report_project17 = ReportProject.objects.create(report=report1, project=project1201_4_001)
		report_project18 = ReportProject.objects.create(report=report1, project=project1201_4_002)
		report_project21 = ReportProject.objects.create(report=report2, project=project1201_1_001)
		report_project22 = ReportProject.objects.create(report=report2, project=project1201_1_002)
		report_project23 = ReportProject.objects.create(report=report2, project=project1201_2_001)
		report_project24 = ReportProject.objects.create(report=report2, project=project1201_2_002)
		report_project25 = ReportProject.objects.create(report=report2, project=project1201_3_001)
		report_project26 = ReportProject.objects.create(report=report2, project=project1201_3_002)
		report_project27 = ReportProject.objects.create(report=report2, project=project1201_4_001)
		report_project28 = ReportProject.objects.create(report=report2, project=project1201_4_002)
		
		# Schedule for Program
		ReportSchedule.objects.create(report_project=report_program11, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program11, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program11, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program13, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program13, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program13, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program14, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program14, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program14, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program21, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program21, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program21, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program22, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program22, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program22, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program23, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program23, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program23, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program24, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program24, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_program24, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		# Schedule for Project
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project13, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project13, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project13, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project14, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project14, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project14, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project15, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project15, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project15, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project16, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project16, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project16, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project17, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project17, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project17, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project18, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project18, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project18, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project23, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project23, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project23, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project24, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project24, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project24, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project25, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project25, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project25, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project26, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project26, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project26, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project27, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project27, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project27, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project28, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_project28, due_date=date(2010, 01, 15))
		ReportSchedule.objects.create(report_project=report_project28, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		
	"""
	END HERE
	"""

# Signal after syncdb
from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb)
