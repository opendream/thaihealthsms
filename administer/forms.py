# -*- encoding: utf-8 -*-
import datetime

from django import forms
from django.forms.util import ErrorList

from domain.forms import SectorChoiceField

from accounts.models import GroupName
from domain.models import Sector, MasterPlan

roles = [(group_name.group.name, group_name.name) for group_name in GroupName.objects.all()]

class UserAccountForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField(label='อีเมล')
	first_name = forms.CharField(max_length=500, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = SectorChoiceField(label='สังกัดสำนัก')
	responsible = forms.IntegerField(widget=forms.HiddenInput(), required=False, label='เลือกแผนหลัก จากนั้นเลือกแผนงานที่รับผิดชอบ')

class ModifySectorForm(forms.Form):
	sector_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	ref_no = forms.IntegerField(label='เลขสำนัก')
	name = forms.CharField(max_length=512, label='ชื่อสำนัก')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		sector_id = cleaned_data.get('sector_id')
		ref_no = cleaned_data.get('ref_no')
		
		if sector_id: existing = Sector.objects.filter(ref_no=ref_no).exclude(id=sector_id).count()
		else: existing = Sector.objects.filter(ref_no=ref_no).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขสำนักนี้ซ้ำกับสำนักอื่น'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class ModifyMasterPlanForm(forms.Form):
	master_plan_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	ref_no = forms.IntegerField(label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อแผน')
	sector = SectorChoiceField(required=True, label='สังกัดสำนัก')

	def clean(self):
		cleaned_data = self.cleaned_data
		master_plan_id = cleaned_data.get('master_plan_id')
		ref_no = cleaned_data.get('ref_no')
		
		if master_plan_id: existing = MasterPlan.objects.filter(ref_no=ref_no).exclude(id=master_plan_id).count()
		else: existing = MasterPlan.objects.filter(ref_no=ref_no).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['รหัสแผนหลักนี้ซ้ำกับแผนหลักอื่น'])
			del cleaned_data['ref_no']
		
		return cleaned_data
