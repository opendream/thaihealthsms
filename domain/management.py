# -*- encoding: utf-8 -*-

# Signal after syncdb
from datetime import datetime, date, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from accounts.models import *
from domain.models import *
from finance.models import *
from kpi.models import *
from report.models import *
from comments.models import *

import calendar
import random

def after_syncdb(sender, **kwargs):

	"""
	THIS IS REAL PRODUCTION CODE
	"""
	
	# Site Information ###############
	Site.objects.all().update(domain=settings.WEBSITE_ADDRESS, name=settings.WEBSITE_ADDRESS)
	
	# User Roles ##################
	#sector_admin_role, created = Group.objects.get_or_create(name='sector_admin')
	#GroupName.objects.get_or_create(group=sector_admin_role, name='ผู้ดูแลระบบของสำนัก')

	sector_manager_role, created = Group.objects.get_or_create(name='sector_manager')
	GroupName.objects.get_or_create(group=sector_manager_role, name='ผู้อำนวยการสำนัก')
	sector_manager_assistant_role, created = Group.objects.get_or_create(name='sector_manager_assistant')
	GroupName.objects.get_or_create(group=sector_manager_assistant_role, name='ผู้ช่วยผู้อำนวยการสำนัก')

	project_manager_role, created = Group.objects.get_or_create(name='project_manager')
	GroupName.objects.get_or_create(group=project_manager_role, name='ผู้จัดการแผนงาน')
	project_manager_assistant_role, created = Group.objects.get_or_create(name='project_manager_assistant')
	GroupName.objects.get_or_create(group=project_manager_assistant_role, name='ผู้ช่วยผู้จัดการแผนงาน')

	# Permission ##################
	# Permission.objects.get_or_create(name='View other projects reports', content_type=ContentType.objects.get_for_model(ReportSchedule), codename='view_others_project_report')

	# Administrator ##################
	admins = settings.ADMINS
	
	from django.core.mail import send_mail
	
	for admin in admins:
		try:
			User.objects.get(username=admin[0])

		except User.DoesNotExist:
			random_password = User.objects.make_random_password()
			#random_password = 'password'
			admin_user = User.objects.create_user(admin[0], admin[1], random_password)
			admin_user.is_superuser = True
			admin_user.is_staff = True
			admin_user.save()
			
			email_render_dict = {'username':admin[0], 'password':random_password, 'settings':settings, 'site_name':settings.WEBSITE_ADDRESS}
			email_subject = render_to_string('email/create_admin_subject.txt', email_render_dict)
			email_message = render_to_string('email/create_admin_message.txt', email_render_dict)
			
			send_mail(email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, [admin[1]])

			admin_account = admin_user.get_profile()
			admin_account.first_name = admin[0]
			admin_account.last_name = ''
			admin_account.save()

	# Master Plan
	default_month_span, created = MonthSpan.objects.get_or_create(start_month=10, is_default=True)
	
	# Comment Receiver by Role
	CommentReceiverRole.objects.create(object_name='project', role=project_manager_role)
	CommentReceiverRole.objects.create(object_name='project', role=project_manager_assistant_role)
	CommentReceiverRole.objects.create(object_name='activity', role=project_manager_role)
	CommentReceiverRole.objects.create(object_name='activity', role=project_manager_assistant_role)
	CommentReceiverRole.objects.create(object_name='report', role=project_manager_role)
	CommentReceiverRole.objects.create(object_name='report', role=project_manager_assistant_role)
	CommentReceiverRole.objects.create(object_name='kpi', role=project_manager_role)
	CommentReceiverRole.objects.create(object_name='kpi', role=project_manager_assistant_role)
	CommentReceiverRole.objects.create(object_name='finance', role=project_manager_role)
	CommentReceiverRole.objects.create(object_name='finance', role=project_manager_assistant_role)

	# Sector ##################
	sector1, created = Sector.objects.get_or_create(ref_no=1, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงหลัก')
	sector2, created = Sector.objects.get_or_create(ref_no=2, name='สำนักสนับสนุนการสร้างสุขภาวะและลดปัจจัยเสี่ยงรอง')
	sector3, created = Sector.objects.get_or_create(ref_no=3, name='สำนักสนับสนุนการสร้างสุขภาวะในพื้นที่ชุมชน')
	sector4, created = Sector.objects.get_or_create(ref_no=4, name='สำนักสนับสนุนการเรียนรู้และสุขภาวะองค์กร')
	sector5, created = Sector.objects.get_or_create(ref_no=5, name='สำนักรณรงค์สื่อสารสาธารณะและสังคม')
	sector6, created = Sector.objects.get_or_create(ref_no=6, name='สำนักสนับสนุนโครงการเปิดรับทั่วไป')
	sector7, created = Sector.objects.get_or_create(ref_no=7, name='สำนักสนับสนุนการพัฒนาระบบสุขภาพและบริการสุขภาพ')

	# Master Plan ##################
	master_plan1, created  = MasterPlan.objects.get_or_create(sector=sector1, ref_no=1, name="แผนควบคุมการบริโภคยาสูบ", month_span=default_month_span)
	master_plan2, created  = MasterPlan.objects.get_or_create(sector=sector1, ref_no=2, name="แผนควบคุมการบริโภคเครื่องดื่มแอลกอฮอล์", month_span=default_month_span)
	master_plan3, created  = MasterPlan.objects.get_or_create(sector=sector1, ref_no=3, name="แผนสนับสนุนการป้องกันอุบัตเหตุทางถนนและอุบัติภัย", month_span=default_month_span)
	master_plan4, created  = MasterPlan.objects.get_or_create(sector=sector2, ref_no=4, name="แผนควบคุมปัจจัยเสี่ยงทางสุขภาพ", month_span=default_month_span)
	master_plan5, created  = MasterPlan.objects.get_or_create(sector=sector2, ref_no=5, name="แผนสุขภาวะประชากรกลุ่มเฉพาะ", month_span=default_month_span)
	master_plan6, created  = MasterPlan.objects.get_or_create(sector=sector3, ref_no=6, name="แผนสุขภาวะชุมชน", month_span=default_month_span)
	master_plan7, created  = MasterPlan.objects.get_or_create(sector=sector4, ref_no=7, name="แผนสุขภาวะเด็ก เยาวชน และครอบครัว", month_span=default_month_span)
	master_plan8, created  = MasterPlan.objects.get_or_create(sector=sector4, ref_no=8, name="แผนสร้างเสริมสุขภาวะในองค์กร", month_span=default_month_span)
	master_plan9, created  = MasterPlan.objects.get_or_create(sector=sector5, ref_no=9, name="แผนส่งเสริมการออกกำลังกายและกีฬาเพื่อสุขภาพ", month_span=default_month_span)
	master_plan10, created  = MasterPlan.objects.get_or_create(sector=sector5, ref_no=10, name="แผนสื่อสารการตลาดเพื่อสังคม", month_span=default_month_span)
	master_plan11, created  = MasterPlan.objects.get_or_create(sector=sector6, ref_no=11, name="แผนสนับสนุนโครงสร้างทั่วไปและนวัตกรรม", month_span=default_month_span)
	master_plan12, created  = MasterPlan.objects.get_or_create(sector=sector7, ref_no=12, name="แผนสนับสนุนการสร้างเสริมสุขภาพผ่านระบบบริการสุขภาพ", month_span=default_month_span)
	master_plan13, created  = MasterPlan.objects.get_or_create(sector=sector7, ref_no=13, name="แผนพัฒนาระบบและกลไกสนับสนุนเพื่อการสร้างเสริมสุขภาพ", month_span=default_month_span)

	"""
	END HERE
	"""

	"""
	BELOW CODE IS FOR PROTOTYPE-PURPOSE ONLY
	"""
	
	if not Project.objects.all():

		# Users ##################
		
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

		# Plan ##################
		plan1201 = Plan.objects.create(master_plan=master_plan12, ref_no="1201", name="กลุ่มแผนงานพัฒนาระบบบริการสุชภาพระดับชุมชน")
		plan1202 = Plan.objects.create(master_plan=master_plan12, ref_no="1202", name="กลุ่มแผนงานพัฒนาระบบกำลังคน")
		plan1203 = Plan.objects.create(master_plan=master_plan12, ref_no="1203", name="กลุ่มแผนงานพัฒนาระบบการสร้างและจัดการความรู้")
		plan1204 = Plan.objects.create(master_plan=master_plan12, ref_no="1204", name="กลุ่มแผนงานการสร้างเสริมสุขภาพและการป้องกันโรค")

		# Project ##################
		project1201_1 = Project.objects.create(master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00001", name="แผนงานที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1201_2 = Project.objects.create(master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00002", name="แผนงานที่สอง", start_date=date(2009,12,16), end_date=date(2011,12,15))
		project1201_3 = Project.objects.create(master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00003", name="แผนงานที่สาม", start_date=date(2008,12,16), end_date=date(2009,12,15))
		project1201_4 = Project.objects.create(master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00004", name="แผนงานที่สี่", start_date=date(2008,12,16), end_date=date(2009,12,15))
		project1201_5 = Project.objects.create(master_plan=master_plan12, plan=plan1201, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="21-00005", name="แผนงานที่ห้า", start_date=date(2010,12,16), end_date=date(2011,12,15))

		project1202_1 = Project.objects.create(master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00001", name="แผนงานที่หก", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1202_2 = Project.objects.create(master_plan=master_plan12, plan=plan1202, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="22-00002", name="แผนงานที่เจ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))

		project1203_1 = Project.objects.create(master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00001", name="แผนงานที่แปด", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1203_2 = Project.objects.create(master_plan=master_plan12, plan=plan1203, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="23-00002", name="แผนงานที่เก้า", start_date=date(2008,12,16), end_date=date(2011,12,15))

		project1204_1 = Project.objects.create(master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00001", name="แผนงานที่สิบ", start_date=date(2008,12,16), end_date=date(2011,12,15))
		project1204_2 = Project.objects.create(master_plan=master_plan12, plan=plan1204, prefix_name=Project.PROJECT_IS_PROGRAM, ref_no="24-00002", name="แผนงานที่สิบเอ็ด", start_date=date(2008,12,16), end_date=date(2011,12,15))

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
		project1201_1_001 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-001", name="โครงการทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,4,1))
		project1201_1_002 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-002", name="โครงการทดลองทีสอง", start_date=date(2009,4,1), end_date=date(2009,8,1))
		project1201_1_003 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-003", name="โครงการทดลองที่สาม", start_date=date(2009,8,1), end_date=date(2009,12,1))
		project1201_1_004 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-004", name="โครงการทดลองที่สี่", start_date=date(2009,12,1), end_date=date(2010,4,1))
		project1201_1_005 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-005", name="โครงการทดลองที่ห้า", start_date=date(2010,4,1), end_date=date(2010,8,1))
		project1201_1_006 = Project.objects.create(master_plan=master_plan12, parent_project=project1201_1, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-006", name="โครงการทดลองที่หก", start_date=date(2010,8,1), end_date=date(2010,12,1))

		project1201_1_005 = Project.objects.create(master_plan=master_plan12, parent_project=None, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-007", name="โครงการทดลองที่เจ็ด", start_date=date(2010,9,1), end_date=date(2010,10,1))
		project1201_1_006 = Project.objects.create(master_plan=master_plan12, parent_project=None, prefix_name=Project.PROJECT_IS_PROJECT, ref_no="21-00001-008", name="โครงการทดลองที่แปด", start_date=date(2010,8,1), end_date=date(2010,10,1))

		# Activity ##################
		activity1 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่หนึ่ง", start_date=date(2008,12,16), end_date=date(2009,3,15))
		activity2 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สอง", start_date=date(2009,3,1), end_date=date(2009,3,16))
		activity3 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สาม", start_date=date(2009,11,16), end_date=date(2009,12,1))
		activity4 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่สี่", start_date=date(2010,6,15), end_date=date(2010, 6,16))
		activity5 = Activity.objects.create(project=project1201_1_001, name="กิจกรรมทดลองที่ห้า", start_date=date(2011,6,14), end_date=date(2011,8,16))

		# KPI ##################		
		opt_category = KPICategory.objects.create(name='Operation')
		opdc_category = KPICategory.objects.create(name='OPDC')
		
		kpi1 = KPI.objects.create(ref_no='1', name='kpi1', category=opt_category, unit_name='unit', master_plan=master_plan12, created_by=sector_manager_assistant_account1)
		kpi2 = KPI.objects.create(ref_no='2', name='kpi2', category=opt_category, unit_name='unit', master_plan=master_plan12, created_by=sector_manager_assistant_account1)
		kpi3 = KPI.objects.create(ref_no='3', name='kpi3', category=opt_category, unit_name='unit', master_plan=master_plan12, created_by=sector_manager_assistant_account1)
		
		kpi101 = KPI.objects.create(ref_no='101', name='kpi101', category=opdc_category, unit_name='unit', created_by=sector_manager_assistant_account1)
		kpi102 = KPI.objects.create(ref_no='102', name='kpi102', category=opdc_category, unit_name='unit', created_by=sector_manager_assistant_account1)
		
		schedule1 = KPISchedule.objects.create(kpi=kpi1, project=project1201_1, target=100, result=30, target_on=date(2010,02,01))
		KPISchedule.objects.create(kpi=kpi1, project=project1201_1, target=100, result= 0, target_on=date(2010,04,01))
		KPISchedule.objects.create(kpi=kpi1, project=project1201_1, target=100, result= 0, target_on=date(2010,06,01))
		
		KPISchedule.objects.create(kpi=kpi2, project=project1201_1, target=100, result=30, target_on=date(2010,02,01))
		KPISchedule.objects.create(kpi=kpi2, project=project1201_1, target=100, result= 0, target_on=date(2010,04,01))
		KPISchedule.objects.create(kpi=kpi2, project=project1201_1, target=100, result= 0, target_on=date(2010,06,01))
		
		KPISchedule.objects.create(kpi=kpi3, project=project1201_1, target=100, result=30, target_on=date(2010,02,01))
		KPISchedule.objects.create(kpi=kpi3, project=project1201_1, target=100, result= 0, target_on=date(2010,04,01))
		KPISchedule.objects.create(kpi=kpi3, project=project1201_1, target=100, result= 0, target_on=date(2010,06,01))
		
		KPISchedule.objects.create(kpi=kpi101, project=project1201_1, target=100, result=30, target_on=date(2010,02,01))
		KPISchedule.objects.create(kpi=kpi101, project=project1201_1, target=100, result= 0, target_on=date(2010,04,01))
		KPISchedule.objects.create(kpi=kpi101, project=project1201_1, target=100, result= 0, target_on=date(2010,06,01))
		
		KPISchedule.objects.create(kpi=kpi102, project=project1201_1, target=100, result=30, target_on=date(2010,02,01))
		KPISchedule.objects.create(kpi=kpi102, project=project1201_1, target=100, result= 0, target_on=date(2010,04,01))
		KPISchedule.objects.create(kpi=kpi102, project=project1201_1, target=100, result= 0, target_on=date(2010,06,01))
		
		KPIScheduleRevision.objects.create(schedule=schedule1, org_target=100, org_result= 0, org_target_on=date(2010,02,01), new_target=100, new_result= 30, new_target_on=date(2010,02,01), revised_on=datetime(2010,01,15,12,00,00), revised_by=sector_manager_assistant_account1)
		#KPIScheduleRevision.objects.create(schedule=schedule1, target=100, result=10, target_on=date(2010,02,01), revised_on=datetime(2010,01,31,12,00,00), revised_by=sector_manager_assistant_account1)
		
		# Finance ##################
		
		finance_schedule = ProjectBudgetSchedule.objects.create(project=project1201_1, target=1000, result=1000, target_on=date(2010,1,1), claimed_on=date(2010,1,1))
		ProjectBudgetSchedule.objects.create(project=project1201_1, target=2000, result=0, target_on=date(2010,6,1))
		ProjectBudgetSchedule.objects.create(project=project1201_1, target=3000, result=0, target_on=date(2010,12,1))
		
		ProjectBudgetScheduleRevision.objects.create(schedule=finance_schedule, org_target=1000, org_result=0, org_target_on=date(2010,1,1), new_target=1000, new_result=500, new_target_on=date(2010,1,1), revised_by=sector_manager_assistant_account1)
	

from django.db.models.signals import post_syncdb
post_syncdb.connect(after_syncdb, dispatch_uid="domain.management")
