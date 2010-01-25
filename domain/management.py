# -*- encoding: utf-8 -*-

# Signal after syncdb
from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

from domain.models import *
from report.models import *
from comments.models import *

import calendar
import random

def after_syncdb(sender, **kwargs):

	"""
	THIS IS REAL PRODUCTION CODE
	"""

	# User Roles ##################
	sector_admin_role, created = Group.objects.get_or_create(name='sector_admin')

	sector_manager_role, created = Group.objects.get_or_create(name='sector_manager')
	sector_manager_assistant_role, created = Group.objects.get_or_create(name='sector_manager_assistant')

	plan_manager_role, created = Group.objects.get_or_create(name='plan_manager')
	plan_manager_assistant_role, created = Group.objects.get_or_create(name='plan_manager_assistant')

	project_manager_role, created = Group.objects.get_or_create(name='project_manager')
	project_manager_assistant_role, created = Group.objects.get_or_create(name='project_manager_assistant')

	# Permission ##################
	# Permission.objects.get_or_create(name='View other projects reports', content_type=ContentType.objects.get_for_model(ReportSchedule), codename='view_others_project_report')

	# Administrator ##################
	admins = settings.ADMINS

	from django.core.mail import send_mail

	for admin in admins:
		try:
			User.objects.get(username=admin[0])

		except User.DoesNotExist:
			#random_password = User.objects.make_random_password()
			random_password = 'password'
			admin_user = User.objects.create_user(admin[0], admin[1], random_password)
			admin_user.is_superuser = True
			admin_user.is_staff = True
			admin_user.save()

			email_content = 'Username: %s\nPassword: %s\n' % (admin[0], random_password)
			# send_mail('Your account for Strategy Management Systems', email_content, settings.SYSTEM_NOREPLY_EMAIL, [admin[1]])

			admin_account = admin_user.get_profile()
			admin_account.first_name = "Administration"
			admin_account.last_name = ""
			admin_account.save()
	
	# Master Plan
	default_month_period, created = MasterPlanMonthPeriod.objects.get_or_create(start_month=10, end_month=9, is_default=True)
	
	"""
	END HERE
	"""

	"""
	BELOW CODE IS FOR PROTOTYPE-PURPOSE ONLY
	"""

	if not Sector.objects.all():

		# Sector ##################
		sector1, created = Sector.objects.get_or_create(ref_no=1, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงหลัก')
		sector2, created = Sector.objects.get_or_create(ref_no=2, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงรอง')
		sector3, created = Sector.objects.get_or_create(ref_no=3, name='สำนักสนับสนุนการสร้างสุขภาวะในพื้นที่ชุมชน')
		sector4, created = Sector.objects.get_or_create(ref_no=4, name='สำนักสนับสนุนการเรียนรู้และสุขภาวะองค์กร')
		sector5, created = Sector.objects.get_or_create(ref_no=5, name='สำนักรณรงค์สื่อสารสาธารณะและสังคม')
		sector6, created = Sector.objects.get_or_create(ref_no=6, name='สำนักสนับสนุนโครงการเปิดรับทั่วไป')
		sector7, created = Sector.objects.get_or_create(ref_no=7, name='สำนักสนับสนุนการพัฒนาระบบสุขภาพและบริการสุขภาพ')

		# Users ##################
		
		# Sector Admin
		sector_admin1 = User.objects.create_user("sector_admin1", "sector_admin1@example.com", "password")
		sector_admin1.groups.add(sector_admin_role)
		
		sector_admin_account1 = sector_admin1.get_profile()
		sector_admin_account1.sector = sector7
		sector_admin_account1.first_name = "Sector"
		sector_admin_account1.last_name = "Admin"
		sector_admin_account1.save()
		
		user_responsibility = UserRoleResponsibility.objects.create(user=sector_admin_account1, role=sector_admin_role)
		
		# Sector Managers
		sector_manager1 = User.objects.create_user("sector7", "sector1@example.com", "password")
		sector_manager1.groups.add(sector_manager_role)

		sector_manager_account1 = sector_manager1.get_profile()
		sector_manager_account1.sector = sector7
		sector_manager_account1.first_name = "เบญจมาภรณ์"
		sector_manager_account1.last_name = "จันทรพัฒน์"
		sector_manager_account1.save()

		user_responsibility = UserRoleResponsibility.objects.create(user=sector_manager_account1, role=sector_manager_role)
		user_responsibility.sectors.add(sector7)

		# Sector Manager Assistants
		sector_manager_assistant1 = User.objects.create_user("pakchuda", "assistant1@example.com", "password")
		sector_manager_assistant1.groups.add(sector_manager_assistant_role)

		sector_manager_assistant_account1 = sector_manager_assistant1.get_profile()
		sector_manager_assistant_account1.sector = sector7
		sector_manager_assistant_account1.first_name = "ภัคชุดา"
		sector_manager_assistant_account1.last_name = "วสุวัต"
		sector_manager_assistant_account1.save()

		# Project Managers
		project_manager1 = User.objects.create_user("project1", "project1@example.com", "password")
		project_manager1.groups.add(project_manager_role)

		project_manager2 = User.objects.create_user("project2", "project2@example.com", "password")
		project_manager2.groups.add(project_manager_role)

		project_manager3 = User.objects.create_user("project3", "project3@example.com", "password")
		project_manager3.groups.add(project_manager_role)

		project_manager_account1 = project_manager1.get_profile()
		project_manager_account1.sector = sector7
		project_manager_account1.first_name = "อภินันท์"
		project_manager_account1.last_name = "อร่ามรัตน์"
		project_manager_account1.save()

		project_manager_account2 = project_manager2.get_profile()
		project_manager_account2.sector = sector7
		project_manager_account2.first_name = "ดร. ยาใจ"
		project_manager_account2.last_name = "สิทธิมงคล"
		project_manager_account2.save()

		project_manager_account3 = project_manager3.get_profile()
		project_manager_account3.sector = sector7
		project_manager_account3.first_name = "จรินทร์"
		project_manager_account3.last_name = "ปภังกรกิจ"
		project_manager_account3.save()

		# Project Manager Assistants
		project_manager_assistant1 = User.objects.create_user("project_assistant1", "project_assistant1@example.com", "password")
		project_manager_assistant1.groups.add(project_manager_assistant_role)

		project_manager_assistant_account1 = project_manager_assistant1.get_profile()
		project_manager_assistant_account1.sector = sector7
		project_manager_assistant_account1.first_name = "Project1"
		project_manager_assistant_account1.last_name = "Assistant"
		project_manager_assistant_account1.save()

		project_manager_assistant2 = User.objects.create_user("project_assistant2", "project_assistant2@example.com", "password")
		project_manager_assistant2.groups.add(project_manager_assistant_role)

		project_manager_assistant_account2 = project_manager_assistant2.get_profile()
		project_manager_assistant_account2.sector = sector7
		project_manager_assistant_account2.first_name = "Project2"
		project_manager_assistant_account2.last_name = "Assistant"
		project_manager_assistant_account2.save()
		
		# Master Plan ##################
		
		year_period = MasterPlanYearPeriod.objects.create(start=date(2008, 10, 1), end=date(2011, 9, 1), month_period=default_month_period)
		
		master_plan1 = MasterPlan.objects.create(sector=sector1, ref_no=1, name="แผนควบคุมการบริโภคยาสูบ", year_period=year_period)
		master_plan2 = MasterPlan.objects.create(sector=sector1, ref_no=2, name="แผนควบคุมการบริโภคเครื่องดื่มแอลกอฮอล์", year_period=year_period)
		master_plan3 = MasterPlan.objects.create(sector=sector1, ref_no=3, name="แผนสนับสนุนการป้องกันอุบัตเหตุทางถนนและอุบัติภัย", year_period=year_period)
		master_plan4 = MasterPlan.objects.create(sector=sector5, ref_no=4, name="แผนส่งเสริมการออกกำลังกายและกีฬาเพื่อสุขภาพ", year_period=year_period)
		master_plan5 = MasterPlan.objects.create(sector=sector2, ref_no=5, name="แผนควบคุมปัจจัยเสี่ยงทางสุขภาพ", year_period=year_period)
		master_plan6 = MasterPlan.objects.create(sector=sector2, ref_no=6, name="แผนสุขภาวะประชากรกลุ่มเฉพาะ", year_period=year_period)
		master_plan7 = MasterPlan.objects.create(sector=sector3, ref_no=7, name="แผนสุขภาวะชุมชน", year_period=year_period)
		master_plan8 = MasterPlan.objects.create(sector=sector4, ref_no=8, name="แผนสุขภาวะเด้ก เยาวชน และครอบครัว", year_period=year_period)
		master_plan9 = MasterPlan.objects.create(sector=sector4, ref_no=9, name="แผนสร้างเสริมสุขภาวะในองค์กร", year_period=year_period)
		master_plan10 = MasterPlan.objects.create(sector=sector5, ref_no=10, name="แผนสื่อสารการตลาดเพื่อสังคม", year_period=year_period)
		master_plan11 = MasterPlan.objects.create(sector=sector6, ref_no=11, name="แผนสนับสนุนโครงสร้างทั่วไปและนวัตกรรม", year_period=year_period)
		master_plan12 = MasterPlan.objects.create(sector=sector7, ref_no=12, name="แผนสนับสนุนการสร้างเสริมสุขภาพผ่านระบบบริการสุขภาพ", year_period=year_period)
		master_plan13 = MasterPlan.objects.create(sector=sector7, ref_no=13, name="แผนพัฒนาระบบและกลไกสนับสนุนเพื่อการสร้างเสริมสุขภาพ", year_period=year_period)
		
		# Plan ##################
		plan1201 = Plan.objects.create(master_plan=master_plan12, ref_no="1201", name="กลุ่มแผนงานพัฒนาระบบบริการสุชภาพระดับชุมชน")
		plan1202 = Plan.objects.create(master_plan=master_plan12, ref_no="1202", name="กลุ่มแผนงานพัฒนาระบบกำลังคน")
		plan1203 = Plan.objects.create(master_plan=master_plan12, ref_no="1203", name="กลุ่มแผนงานพัฒนาระบบการสร้างและจัดการความรู้")
		plan1204 = Plan.objects.create(master_plan=master_plan12, ref_no="1204", name="กลุ่มแผนงานการสร้างเสริมสุขภาพและการป้องกันโรค")
		
		# Project ##################
		project1201_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00001", name="แผนงานที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1201_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00002", name="แผนงานที่สอง", start_date=date(2009,12,16), end_date=date(2011,12,15))
		project1201_3 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00003", name="แผนงานที่สาม", start_date=date(2008,12,16), end_date=date(2009,12,15))
		project1201_4 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00004", name="แผนงานที่สี่", start_date=date(2008,12,16), end_date=date(2009,12,15))
		project1201_5 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00005", name="แผนงานที่ห้า", start_date=date(2010,12,16), end_date=date(2011,12,15))

		project1202_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00001", name="แผนงานที่หก", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1202_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00002", name="แผนงานที่เจ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))

		project1203_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00001", name="แผนงานที่แปด", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1203_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00002", name="แผนงานที่เก้า", start_date=date(2008,12,16), end_date=date(2011,12,15))

		project1204_1 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00001", name="แผนงานที่สิบ", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1204_2 = Project.objects.create(sector=sector7, master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00002", name="แผนงานที่สิบเอ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))

		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_account1, role=project_manager_role)
		user_responsibility.projects.add(project1201_1)
		user_responsibility.projects.add(project1202_1)
		user_responsibility.projects.add(project1204_1)
		user_responsibility.projects.add(project1204_2)

		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_account2, role=project_manager_role)
		user_responsibility.projects.add(project1201_2)
		user_responsibility.projects.add(project1201_4)
		user_responsibility.projects.add(project1201_5)
		user_responsibility.projects.add(project1203_1)

		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_account3, role=project_manager_role)
		user_responsibility.projects.add(project1201_3)
		user_responsibility.projects.add(project1202_2)
		user_responsibility.projects.add(project1203_2)

		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_assistant_account1, role=project_manager_assistant_role)
		user_responsibility.projects.add(project1201_1)
		user_responsibility.projects.add(project1201_3)
		user_responsibility.projects.add(project1202_1)
		user_responsibility.projects.add(project1202_2)
		user_responsibility.projects.add(project1204_1)
		user_responsibility.projects.add(project1204_2)

		user_responsibility = UserRoleResponsibility.objects.create(user=project_manager_assistant_account2, role=project_manager_assistant_role)
		user_responsibility.projects.add(project1201_2)
		user_responsibility.projects.add(project1201_4)
		user_responsibility.projects.add(project1201_5)
		user_responsibility.projects.add(project1203_1)
		user_responsibility.projects.add(project1203_2)
		
		user_responsibility = UserRoleResponsibility.objects.create(user=sector_manager_assistant_account1, role=sector_manager_assistant_role)
		user_responsibility.projects.add(project1201_1)
		user_responsibility.projects.add(project1201_2)
		user_responsibility.projects.add(project1201_3)
		
		# Project ##################
		project1201_1_001 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-001", name="โครงการทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,4,1))
		project1201_1_002 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-002", name="โครงการทดลองทีสอง", start_date=date(2009,4,1), end_date=date(2009,8,1))
		project1201_1_003 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-003", name="โครงการทดลองที่สาม", start_date=date(2009,8,1), end_date=date(2009,12,1))
		project1201_1_004 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-004", name="โครงการทดลองที่สี่", start_date=date(2009,12,1), end_date=date(2010,4,1))
		project1201_1_005 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-005", name="โครงการทดลองที่ห้า", start_date=date(2010,4,1), end_date=date(2010,8,1))
		project1201_1_006 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-006", name="โครงการทดลองที่หก", start_date=date(2010,8,1), end_date=date(2010,12,1))
		
		project1201_1_005 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=None, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-007", name="โครงการทดลองที่เจ็ด", start_date=date(2010,9,1), end_date=date(2010,10,1))
		project1201_1_006 = Project.objects.create(sector=sector7, master_plan=master_plan12, parent_project=None, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-008", name="โครงการทดลองที่แปด", start_date=date(2010,8,1), end_date=date(2010,10,1))
		
		# Activity ##################
		activity1 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,3,15))
		activity2 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สอง", start_date=date(2009,3,1), end_date=date(2009,3,16))
		activity3 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สาม", start_date=date(2009,11,16), end_date=date(2009,12,1))
		activity4 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สี่", start_date=date(2010,6,15), end_date=date(2010, 6,16))
		activity5 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่ห้า", start_date=date(2011,6,14), end_date=date(2011,8,16))

		user_responsibility.activities.add(activity1)
		user_responsibility.activities.add(activity2)
		user_responsibility.activities.add(activity3)
		user_responsibility.activities.add(activity4)
		user_responsibility.activities.add(activity5)


		# Report ##################
		report1 = Report.objects.create(name="รายงานความก้าวหน้าประจำเดือน",
										created_by=sector_manager_account1,
										sector=sector7,
										need_checkup=True,
										need_approval=True,)

		report2 = Report.objects.create(name="รายงานการเงินประจำเดือน",
										created_by=sector_manager_account1,
										sector=sector7,
										need_checkup=True,)
		
		report_project11 = ReportProject.objects.create(report=report1, project=project1201_1)
		report_project12 = ReportProject.objects.create(report=report2, project=project1201_1)
		
		
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(21))
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(14))
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(7), submitted_on=datetime.now(), state=SUBMIT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(-7), submitted_on=datetime.now(), state=SUBMIT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(-14), submitted_on=datetime.now(), state=SUBMIT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(-21), submitted_on=datetime.now(), state=APPROVE_ACTIVITY, approval_on=datetime.now())
		
		
		"""
		# Next due
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(16))
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(32))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() + timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() + timedelta(32))
		
		# Late
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(16))
		
		# Rejected
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(4), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(4), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)

		# Approved
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)

		report_project11 = ReportProject.objects.create(report=report1, project=project1201_1)
		report_project12 = ReportProject.objects.create(report=report2, project=project1201_1)

		# Next due
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() + timedelta(32))

		# Late
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(16))

		# Submitted
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(4), submitted_on=date.today())

		# Rejected
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(4), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)

		# Approved
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)

		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)


		report_project11 = ReportProject.objects.create(report=report1, project=project1201_2)
		report_project12 = ReportProject.objects.create(report=report2, project=project1201_2)


		# Next due
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() + timedelta(32))

		# Late
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(16))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(16))

		# Rejected
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(4), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(4), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)

		# Approved
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)

		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)

		report_project11 = ReportProject.objects.create(report=report1, project=project1201_1_001)
		report_project12 = ReportProject.objects.create(report=report2, project=project1201_1_001)

		# Next due
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(32))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() + timedelta(16))

		# Late
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(17))
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(17))

		# Rejected
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() + timedelta(5), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(5), submitted_on=date.today(), last_activity=REJECT_ACTIVITY)

		# Approved
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project11, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)

		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(30), submitted_on=date.today() - timedelta(31), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(60), submitted_on=date.today() - timedelta(61), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(90), submitted_on=date.today() - timedelta(91), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(120), submitted_on=date.today() - timedelta(121), last_activity=APPROVE_ACTIVITY)
		ReportSchedule.objects.create(report_project=report_project12, due_date=date.today() - timedelta(150), submitted_on=date.today() - timedelta(151), last_activity=APPROVE_ACTIVITY)
		"""
		
		# Comment Receiver by Role
		CommentReceiverRole.objects.create(object_name='project', role=project_manager_role)
		CommentReceiverRole.objects.create(object_name='project', role=project_manager_assistant_role)

from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="domain.management")
