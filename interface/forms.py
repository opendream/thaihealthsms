# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.formtools.wizard import FormWizard
from django.contrib.admin import widgets
from django.contrib.auth.models import User, Group
from domain.models import *

from django.http import HttpResponseRedirect
from helper.utilities import set_message

class AddActivityForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date 		= forms.DateField(widget=widgets.AdminDateWidget, label='เริ่ม')
	end_date 		= forms.DateField(widget=widgets.AdminDateWidget, label='ถึง')
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')

sectors = [(sector.id, '%s %s' % (sector.ref_no, sector.name)) for sector in Sector.objects.all()]
roles = [(group.name, group.name) for group in Group.objects.all()]
class UserAccountFormStart(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput(), label='รหัสผ่าน')
	password_confirm = forms.CharField(widget=forms.PasswordInput(), label='ยืนยันรหัสผ่าน')
	first_name = forms.CharField(max_length=500, required=False, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, required=False, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = forms.IntegerField(widget=forms.Select(choices=sectors), label='สังกัดสำนัก')

	def clean_password_confirm(self):
		password = self.cleaned_data.get('password', '')
		password_confirm = self.cleaned_data.get('password_confirm', '')

		if not password or password != password_confirm:
			raise forms.ValidationError('Password not match')
		return password

	def clean_project(self):
		return self.cleaned_data.get('project', [])
		
class UserAccountFormSecond(forms.Form):
	pass
	
class UserAccountWizard(FormWizard):
	def done(self, request, form_list):
		form = {}
		for form_item in form_list:
			form.update(form_item.cleaned_data)
			
		sector = Sector.objects.get(id=form.get('sector', 0))
		print sector.id
			
		user = User.objects.create_user(form.get('username', ''), form.get('email', ''), form.get('password', ''))
		
		user_account = user.get_profile()
		user_account.first_name = form.get('first_name', ''),
		user_account.last_name = form.get('last_name', ''),
		user_account.sector = sector
		user_account.save()

		group_name = form.get('role', '')
		user_responsibility = UserRoleResponsibility.objects.create(
			user = user_account, 
			role = Group.objects.get(name=group_name)			
		)

		if group_name == 'sector_manager':
			user_responsibility.sectors.add(sector)
		elif group_name == 'sector_manager_assistant':
			user_responsibility.sectors.add(sector)
			for project in Project.objects.filter(pk__in=form.get('project', [])):
				user_responsibility.projects.add(project)
		elif group_name in ('program_manager', 'program_manager_assistant'):
			program = Project.objects.get(pk=form.get('program', 0))
			user_responsibility.projects.add(program)
		
		
		set_message(request, 'Your user has been create.')
		return HttpResponseRedirect('/administer/users/')
	
	def get_template(self, step):
		return 'administer_users_add.html'
		
	def process_step(self, request, form, step):		
		if step == 0 and form.is_valid():
			group_name = form.cleaned_data.get('role', '')			
			sector_id = form.cleaned_data.get('sector', 0)
			
			if group_name == 'sector_manager':
				self.form_list[1] = UserAccountFormSecond
			elif group_name == 'sector_manager_assistant':
				projects_obj = Project.objects.filter(sector__id=sector_id, prefix_name=Project.PROJECT_IS_PROJECT, parent_project=None)
				projects = [(project.id, '%s %s' % (project.ref_no, project.name)) for project in projects_obj]
				
				class UserAccountFormForSector(forms.Form):
					project = forms.MultipleChoiceField(choices=projects, required=False, label='โครงการ')
					
				self.form_list[1] = UserAccountFormForSector
				
			elif group_name in ('program_manager', 'program_manager_assistant'):
				programs_obj = Project.objects.filter(sector__id=sector_id, prefix_name=Project.PROJECT_IS_PROGRAM)
				programs = [(program.id, '%s %s' % (program.ref_no, program.name)) for program in programs_obj]
				
				class UserAccountFormForProgram(forms.Form):
					program = forms.IntegerField(widget=forms.Select(choices=programs), required=False, label='แผนงาน')
			
				self.form_list[1] = UserAccountFormForProgram

		
		
		
		
		
		
		
		
		
		