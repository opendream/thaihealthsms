# -*- encoding: utf-8 -*-
import datetime

from django import forms
from django.forms.util import ErrorList
from django.contrib.formtools.wizard import FormWizard
from django.contrib.admin import widgets
from django.contrib.auth.models import User, Group
from domain.models import *
from report.models import *

from django.http import HttpResponseRedirect
from helper.utilities import set_message

from widgets import YUICalendar

month_cycle = [(i,i) for i in range(1,13)]
date_cycle = [(0, 'วันสิ้นเดือน'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20),(21,21),(22,22),(23,23),(24,24),(25,25),(26,26),(27,27),(28,28),(29,29),(30,30),(31,31)]

sectors = [(sector.id, '%s %s' % (sector.ref_no, sector.name)) for sector in Sector.objects.all().order_by('ref_no')]
roles = [(group_name.group.name, group_name.name) for group_name in GroupName.objects.all()]

class UserAccountForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField(label='อีเมล')
	first_name = forms.CharField(max_length=500, required=False, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, required=False, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = forms.IntegerField(widget=forms.Select(choices=sectors), label='สังกัดสำนัก')
	responsible = forms.IntegerField(widget=forms.HiddenInput(), required=False, label='เลือกแผนหลัก จากนั้นเลือกแผนงานที่รับผิดชอบ')

class ChangeFirstTimePasswordForm(forms.Form):
	password1 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่าน')
	password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='ยืนยันรหัสผ่าน')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		
		if password1 != password2:
			self._errors["password2"] = ErrorList(['รหัสผ่านไม่สัมพันธ์กัน'])
			del cleaned_data["password2"]
		
		return cleaned_data

class ChangePasswordForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	old_password = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่านเก่า')
	new_password1 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่านใหม่')
	new_password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='ยืนยันรหัสผ่านใหม่')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		username = cleaned_data.get('username')
		old_password = cleaned_data.get('old_password')
		new_password1 = cleaned_data.get('new_password1')
		new_password2 = cleaned_data.get('new_password2')
		
		if new_password1 != new_password2:
			self._errors["new_password2"] = ErrorList(['รหัสผ่านไม่สัมพันธ์กัน'])
			del cleaned_data["new_password2"]
		
		from django.contrib.auth.models import User
		
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			self._errors["username"] = ErrorList(['ไม่พบผู้ใช้นี้ในระบบ'])
			del cleaned_data["username"]
		else:
			from django.contrib.auth.models import check_password
			
			if not check_password(old_password, user.password):
				self._errors["old_password"] = ErrorList(['รหัสผ่านไม่ถูกต้อง'])
				del cleaned_data["old_password"]
		
		return cleaned_data

"""
class UserAccountFormStart(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput(),required=False, label='รหัสผ่าน')
	password_confirm = forms.CharField(widget=forms.PasswordInput(),required=False, label='ยืนยันรหัสผ่าน')
	first_name = forms.CharField(max_length=500, required=False, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, required=False, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = forms.IntegerField(widget=forms.Select(choices=sectors), label='สังกัดสำนัก')

	def clean_password_confirm(self):
		password = self.cleaned_data.get('password', '')
		password_confirm = self.cleaned_data.get('password_confirm', '')

		if password != password_confirm:
			raise forms.ValidationError('Password not match')
		return password

	def clean_project(self):
		return self.cleaned_data.get('project', [])

class UserAccountFormSecond(forms.Form):
	pass

class UserAccountWizard(FormWizard):
	def parse_params(self, request, *args, **kwargs):
		user_id = kwargs.get('user_id', 0)

		self.user = False
		if user_id:
			user = User.objects.get(pk=user_id)
			self.user = user
			user_account = user.get_profile()
			user_responsibility = UserRoleResponsibility.objects.get(user=user_account)

			initial = {}

			initial[0] = user.__dict__.copy()
			initial[0].update(user_account.__dict__.copy())
			initial[0].update(user_responsibility.__dict__.copy())

			initial[0]['password'] = ''
			initial[0]['sector'] = user_account.sector.id
			initial[0]['role'] = user_responsibility.role.name

			initial[1] = {}
			if user_responsibility.projects.count():
				initial[1]['program'] = user_responsibility.projects.all()[0].id
				initial[1]['project'] = [project.id for project in user_responsibility.projects.all()]

			self.initial = initial

	def get_template(self, step):
		return 'administer_users_add.html'

	def process_step(self, request, form, step):
		if step == 0 and form.is_valid():
			group_name = form.cleaned_data.get('role', '')
			sector_id = form.cleaned_data.get('sector', 0)

			if group_name == 'sector_admin' or group_name == 'sector_manager':
				if len(self.form_list) > 1:
					del(self.form_list[1])

			elif group_name == 'sector_manager_assistant':
				projects_obj = Project.objects.filter(sector__id=sector_id, prefix_name=Project.PROJECT_IS_PROJECT, parent_project=None)
				projects = [(project.id, '%s %s' % (project.ref_no, project.name)) for project in projects_obj]

				class UserAccountFormForSector(forms.Form):
					project = forms.MultipleChoiceField(choices=projects, required=False, label='โครงการ')

				if len(self.form_list) == 1:
					self.form_list.append(UserAccountFormForSector)
				else:
					self.form_list[1] = UserAccountFormForSector

			elif group_name in ('project_manager', 'project_manager_assistant'):
				programs_obj = Project.objects.filter(sector__id=sector_id, prefix_name=Project.PROJECT_IS_PROGRAM)
				programs = [(program.id, '%s %s' % (program.ref_no, program.name)) for program in programs_obj]

				class UserAccountFormForProgram(forms.Form):
					program = forms.IntegerField(widget=forms.Select(choices=programs), required=False, label='แผนงาน')

				if len(self.form_list) == 1:
					self.form_list.append(UserAccountFormForProgram)
				else:
					self.form_list[1] = UserAccountFormForProgram

	def done(self, request, form_list):
		form = {}
		for form_item in form_list:
			form.update(form_item.cleaned_data)

		sector = Sector.objects.get(id=form.get('sector', 0))

		if self.user:
			user = self.user
			user.username = form.get('username', '')
			user.email = form.get('email', '')

			password = form.get('password', '')
			if password:
				user.set_password(password)

			user.save()
		else:
			user = User.objects.create_user(form.get('username', ''), form.get('email', ''), form.get('password', ''))

		user_account = user.get_profile()
		user_account.first_name = form.get('first_name', ''),
		user_account.last_name = form.get('last_name', ''),
		user_account.sector = sector
		user_account.save()

		group_name = form.get('role', '')
		if self.user:
			user_responsibility = UserRoleResponsibility.objects.filter(user=user_account).delete()

		user_responsibility = UserRoleResponsibility.objects.create(
			user = user_account,
			role = Group.objects.get(name=group_name)
		)


		if group_name == 'sector_admin' or group_name == 'sector_manager':
			user_responsibility.sectors.add(sector)
		elif group_name == 'sector_manager_assistant':
			user_responsibility.sectors.add(sector)
			for project in Project.objects.filter(pk__in=form.get('project', [])):
				user_responsibility.projects.add(project)
		elif group_name in ('project_manager', 'project_manager_assistant'):
			program = Project.objects.get(pk=form.get('program', 0))
			user_responsibility.projects.add(program)

		if self.user:
			set_message(request, 'Your user has been update.')
		else:
			set_message(request, 'Your user has been create.')

		return HttpResponseRedirect('/administer/users/')
"""
class SectorChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return "%d %s" % (obj.id, obj.name)

class MasterPlanForm(forms.Form):
	'''MasterPlan adding form'''

	ref_no = forms.IntegerField(label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อแผน')
	sector = SectorChoiceField(required=True, queryset=Sector.objects.all().order_by('ref_no'), empty_label=None, label='สังกัดสำนัก')
	year_start = forms.IntegerField(label='ช่วงปี')
	year_end = forms.IntegerField(label='ถึง')

	def clean(self):
		"Check if year_start and year_end is valid."

		cleaned_data = self.cleaned_data
		year_start = cleaned_data.get('year_start')
		year_end = cleaned_data.get('year_end')

		# Convert B.E. to C.E.
		thai_year_start = year_start - 543
		thai_year_end = year_end - 543
		try:
			thai_date_start = datetime.date(thai_year_start, 1, 1)
			thai_date_end = datetime.date(thai_year_end, 1, 1)

			if thai_date_start > thai_date_end:
				raise forms.ValidationError("Start year must greater than end year")
		except ValueError:
			raise forms.ValidationError("Year is not valid.")

		return cleaned_data

class EditMasterPlanForm(forms.Form):
	ref_no = forms.IntegerField(label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อแผน')
	sector = forms.IntegerField(widget=forms.Select(choices=sectors), label='สังกัดสำนัก')

#
# Sector Form
#
class SectorForm(forms.Form):
	ref_no = forms.IntegerField(label='เลขสำนัก')
	name = forms.CharField(max_length=512, label='ชื่อสำนัก')

class SectorReportForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อรายงาน')
	need_approval = forms.BooleanField(required=False, label='รายงานที่ส่งมา ต้องมีการรับรองรายงาน')
	schedule_cycle_length = forms.ChoiceField(choices=month_cycle)
	schedule_monthly_date = forms.ChoiceField(choices=date_cycle)

#
# Master Plan Form
#
class MasterPlanAddProjectForm(forms.Form):
	plan = PlanChoiceField(queryset=Plan.objects.all(), label="สังกัดกลุ่มแผนงาน", empty_label=None)
	ref_no = forms.CharField(max_length=64, label='เลขที่โครงการ')
	name = forms.CharField(max_length=512, label='ชื่อโครงการ')
	description = forms.CharField(widget=forms.Textarea(), required=False, label='รายละเอียด')
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่ม')
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')
	reports = ReportMultipleChoiceField(queryset=Report.objects.all(), label="รายงานที่ต้องส่ง")

class MasterPlanEditProjectForm(forms.Form):
	plan = PlanChoiceField(queryset=Plan.objects.all(), label="สังกัดกลุ่มแผนงาน", empty_label=None)
	ref_no = forms.CharField(max_length=64, label='เลขที่โครงการ')
	name = forms.CharField(max_length=512, label='ชื่อโครงการ')
	description = forms.CharField(widget=forms.Textarea(), required=False, label='รายละเอียด')

#
# Plan Form
#
class PlanForm(forms.Form):
	ref_no = forms.CharField(max_length=512, label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อกลุ่มแผนงาน')

class PlanChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, obj):
		return "%s %s" % (obj.ref_no, obj.name)

class ReportMultipleChoiceField(forms.ModelMultipleChoiceField):
	def label_from_instance(self, obj):
		return "%s" % obj.name

#
# Project Form
#
class ProjectForm(forms.Form):
	ref_no = forms.CharField(max_length=64, label='เลขที่โครงการ')
	name = forms.CharField(max_length=512, label='ชื่อโครงการ')
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลาโครงการ')
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')

class AddProjectReportForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อรายงาน')
	need_checkup = forms.BooleanField(required=False, label='ส่งรายงานถึงผู้ประสานงานสำนัก')
	need_approval = forms.BooleanField(required=False, label='ต้องรับรองรายงาน')
	schedule_cycle_length = forms.ChoiceField(choices=month_cycle)
	schedule_monthly_date = forms.ChoiceField(choices=date_cycle)
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่มตั้งแต่วันที่')
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')

class EditProjectReportForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อรายงาน')

#
# Activity Form
#
class ActivityForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date      = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่มตั้งแต่วันที่', required=False)
	end_date        = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')
