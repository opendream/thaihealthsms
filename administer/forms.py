# -*- encoding: utf-8 -*-
import datetime

from django import forms

from domain.forms import SectorChoiceField

from accounts.models import GroupName
from domain.models import Sector

roles = [(group_name.group.name, group_name.name) for group_name in GroupName.objects.all()]

class UserAccountForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	email = forms.EmailField(label='อีเมล')
	first_name = forms.CharField(max_length=500, required=False, label='ชื่อจริง')
	last_name = forms.CharField(max_length=500, required=False, label='นามสกุล')
	role = forms.CharField(widget=forms.Select(choices=roles), label='ตำแหน่ง')
	sector = SectorChoiceField(required=True, label='สังกัดสำนัก')
	responsible = forms.IntegerField(widget=forms.HiddenInput(), required=False, label='เลือกแผนหลัก จากนั้นเลือกแผนงานที่รับผิดชอบ')

class ModifySectorForm(forms.Form):
	ref_no = forms.IntegerField(label='เลขสำนัก')
	name = forms.CharField(max_length=512, label='ชื่อสำนัก')

class ModifyMasterPlanForm(forms.Form):
	ref_no = forms.IntegerField(label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อแผน')
	sector = SectorChoiceField(required=True, label='สังกัดสำนัก')
