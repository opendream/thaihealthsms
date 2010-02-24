# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

from models import KPICategory, KPI

from domain.models import MasterPlan
from domain.forms import MasterPlanChoiceField

# FIELD CLASSES

class KPICategoryChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = KPICategory.objects.all()
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return obj.name

# FORM CLASSES

class ModifyKPIForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector: self.fields["master_plan"].queryset = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
		else: self.fields["master_plan"].required = False
	
	kpi_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	master_plan = MasterPlanChoiceField(required=True, label='แผนหลัก')
	ref_no = forms.CharField(max_length=512, label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อตัวชี้วัด')
	category = KPICategoryChoiceField(required=True, label='ประเภท')
	unit_name = forms.CharField(max_length=512, label='หน่วยที่ใช้วัด')
	visible_to_project = forms.BooleanField(required=False, label='ให้แผนงานมองเห็นข้อมูลตัวชี้วัดนี้')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		
		master_plan = cleaned_data.get('master_plan')
		kpi_id = cleaned_data.get('kpi_id')
		ref_no = cleaned_data.get('ref_no')
		
		if not master_plan:
			if kpi_id: existing = KPI.objects.filter(ref_no=ref_no, master_plan=None).exclude(id=kpi_id).count()
			else: existing = KPI.objects.filter(ref_no=ref_no, master_plan=None).count()
			
			if existing:
				self._errors['ref_no'] = ErrorList(['รหัสตัวชี้วัดนี้ซ้ำกับตัวชี้วัดอื่นๆขององค์กร'])
				del cleaned_data['ref_no']
			
		else:
			if kpi_id: existing = KPI.objects.filter(ref_no=ref_no, master_plan=master_plan).exclude(id=kpi_id).count()
			else: existing = KPI.objects.filter(ref_no=ref_no, master_plan=master_plan).count()
			
			if existing:
				self._errors['ref_no'] = ErrorList(['รหัสตัวชี้วัดนี้ซ้ำกับตัวชี้วัดอื่นๆภายในแผน'])
				del cleaned_data['ref_no']
		
		return cleaned_data

class ModifyKPICategoryForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อประเภท')

class ModifyKPIRemarkForm(forms.Form):
	remark = forms.CharField(max_length=1000, widget=forms.Textarea(), label='หมายเหตุ')
