# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.admin import widgets

class AddActivityForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date 		= forms.DateField(widget=widgets.AdminDateWidget, label='เริ่ม')
	end_date 		= forms.DateField(widget=widgets.AdminDateWidget, label='ถึง')
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')