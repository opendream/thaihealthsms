# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import User, Group
from domain.models import *

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
class UserAccountForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput(), label='รหัสผ่าน')
	password_confirm = forms.CharField(widget=forms.PasswordInput(), label='ยืนยันรหัสผ่าน')
	first_name = forms.CharField(max_length=500, required=False, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, required=False, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = forms.IntegerField(widget=forms.Select(choices=sectors), label='สังกัดสำนัก')
	program = forms.IntegerField(widget=forms.Select(), required=False, label='แผนงาน')
	project = forms.MultipleChoiceField(required=False, label='โครงการ')

	def clean_password_confirm(self):
		password = self.cleaned_data.get('password', '')
		password_confirm = self.cleaned_data.get('password_confirm', '')

		if not password or password != password_confirm:
			raise forms.ValidationError('Password not match')
		return password

	def clean_project(self):
		return self.cleaned_data.get('project', [])
