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
		assistant_account1.first_name = "ภัคชุดา"
		assistant_account1.last_name = "วสุวัต"
		assistant_account1.save()
		
		# Sector Managers
		sector_manager1 = User.objects.create_user("sector1", "sector1@example.com", "password")
		
		sector_manager_account1 = sector_manager1.get_profile()
		sector_manager_account1.role = "sector_manager"
		sector_manager_account1.sector = sector7
		sector_manager_account1.first_name = "เบญจมาภรณ์"
		sector_manager_account1.last_name = "จันทรพัฒน์"
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
		plan1204 = Plan.objects.create(master_plan=master_plan12, ref_no="1204", name="กลุ่มแผนงานพัฒนาระบบสุขภาพชุมชน")
		plan1201 = Plan.objects.create(master_plan=master_plan12, ref_no="1201", name="กลุ่มแผนงานพัฒนาบุคลากรสุขภาพ")
		plan1202 = Plan.objects.create(master_plan=master_plan12, ref_no="1202", name="กลุ่มแผนงานการสร้างและจัดการความรู้")
		plan1203 = Plan.objects.create(master_plan=master_plan12, ref_no="1203", name="กลุ่มแผนงานพัฒนาระบบกลไกการจัดการบริการสร้างเสริมสุขภาพและป้องกันโรครูปแบบต่างๆ")
		
		plan1301 = Plan.objects.create(master_plan=master_plan13, ref_no="1301", name="กลุ่มแผนงาน 1301")
		plan1302 = Plan.objects.create(master_plan=master_plan13, ref_no="1302", name="กลุ่มแผนงาน 1302")
		
		# Program
		program1204_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, type=Project.PROGRAM_TYPE, ref_no="51-02415", name="แผนงานพัฒนาระบบสุขภาพชุมชน โดยชุมชน เพื่อชุมชน", manager=program_manager_account1, start_date=date(2008,12,16), end_date=date(2011,12,15))
		
		program1201_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="51-00792", name="แผนงานโรงเรียนทันตแพทย์สร้างสุข", manager=program_manager_account2, start_date=date(2008,6, 1), end_date=date(2011,6,30))
		program1201_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="50-00919", name="แผนงานเครือข่ายเภสัชศาสตร์เพื่อการสร้างเสริมสุขภาพ ระยะที่ 2", manager=program_manager_account1, start_date=date(2007,6,1), end_date=date(2010,6,30))
		program1201_3 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="51-00792", name="แผนงานพัฒนาสถาบันการศึกษาสาธารณสุขศาสตร์ให้เป็นองค์กรสร้างเสริมสุขภาพ", manager=program_manager_account2, start_date=date(2008,7,1), end_date=date(2011,5,31))
		program1201_4 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="51-02827", name="แผนงานพัฒนากำลังคนด้านสุขภาพ", manager=program_manager_account1, start_date=date(2008,1,1), end_date=date(2011,12,31))
		program1201_5 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="52-00133", name="แผนงานโรงเรียนแพทย์สร้างเสริมสุขภาพ", manager=program_manager_account2, start_date=date(2009,1,5), end_date=date(2009,12,31))
		program1201_6 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="51-00604", name="แผนงานพัฒนาเครือข่ายพยาบาลศาสตร์เพื่อการสร้างเสริมสุขภาพ", manager=program_manager_account1, start_date=date(2008,5,1), end_date=date(2011,1,15))
		
		program1202_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="49-01761", name="แผนงานพัฒนาต้นแบบการดำเนินงานสร้างเสริมสุขภาพในบริบทของพยาบาล ระยะที่ 2", manager=program_manager_account2, start_date=date(2007,1,1), end_date=date(2011,6,30))
		
		program1204_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, type=Project.PROGRAM_TYPE, ref_no="", name="แผนงานนโยบายระบบสุขภาพชุมชน", manager=program_manager_account1)
		
		program1201_7 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, type=Project.PROGRAM_TYPE, ref_no="53-00061", name="แผนงานโรงเรียนแพทย์สร้างเสริมสุขภาพ", manager=program_manager_account2)
		
		program1202_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="", name="แผนงานพัฒนาเครือข่ายหมออนามัย", manager=program_manager_account1)
		program1202_3 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="", name="แผนงานสร้างเสริมสุขภาพโดยเครือข่ายสหวิชาชีพด้านสุขภาพ", manager=program_manager_account2)
		program1202_4 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, type=Project.PROGRAM_TYPE, ref_no="", name="แผนงานพัฒนาองค์ความรู้เพื่อการสร้างเสริมสุขภาพโดยพยาบาลชุมชน", manager=program_manager_account2)
		
		
		# Project
		project1204_1_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1204_1, type=Project.PROJECT_TYPE, ref_no="51-02415-001", name="โครงการทดลองที่ 1", manager=project_manager_account1, start_date=date(2008,12,16), end_date=date(2009,12,1))
		project1204_1_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=program1204_1, type=Project.PROJECT_TYPE, ref_no="51-02415-002", name="โครงการทดลองที่ 2", manager=project_manager_account2, start_date=date(2010, 1, 15), end_date=date(2011,12, 15))
		
		# Assist Projects
		assistant_account1.projects.add(program1204_1)
		assistant_account1.projects.add(program1201_1)
		assistant_account1.projects.add(program1201_2)
		assistant_account1.projects.add(program1202_1)
		
		# Activity
		activity1 = Activity.objects.create(project=project1204_1_001, name="กิจกรรมทดลอง 1", start_date=date(2008,12,16), end_date=date(2009,3,15))
		activity2 = Activity.objects.create(project=project1204_1_001, name="กิจกรรมทดลอง 2", start_date=date(2009,3,1), end_date=date(2009,3,16))
		activity3 = Activity.objects.create(project=project1204_1_001, name="กิจกรรมทดลอง 3", start_date=date(2009,11,16), end_date=date(2009,12,1))
		activity4 = Activity.objects.create(project=project1204_1_002, name="กิจกรรมทดลอง 4", start_date=date(2010,6,15), end_date=date(2010, 6,16))
		activity5 = Activity.objects.create(project=project1204_1_002, name="กิจกรรมทดลอง 5", start_date=date(2011,6,14), end_date=date(2011,8,16))
		
		
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
		ReportSchedule.objects.create(report_project=report_program11, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 02, 15))
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2010, 01, 15), is_submitted=True, submitted=datetime.now())
		ReportSchedule.objects.create(report_project=report_program12, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		# Schedule for Project
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 11, 15), is_submitted=True, submitted=datetime.now())
		ReportSchedule.objects.create(report_project=report_project11, due_date=date(2009, 10, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 11, 15), is_submitted=True, submitted=datetime.now())
		ReportSchedule.objects.create(report_project=report_project12, due_date=date(2009, 12, 15), is_submitted=True, submitted=datetime.now())
		
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  3, 15))
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  2, 15))
		ReportSchedule.objects.create(report_project=report_project21, due_date=date(2010,  1, 15))
		
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  3, 15))
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  2, 15))
		ReportSchedule.objects.create(report_project=report_project22, due_date=date(2010,  1, 15), is_submitted=True, submitted=datetime.now())

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
	END HERE
	"""

# Signal after syncdb
from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb)
