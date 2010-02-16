# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

from report.forms import ReportChoiceField

from domain.models import Sector, MasterPlan, Plan
from report.models import Report

from widgets import YUICalendar

# FIELD CLASSES

class SectorChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Sector.objects.all().order_by('ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return '%d %s' % (obj.ref_no, obj.name)

class MasterPlanChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = MasterPlan.objects.all().order_by('ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return '%d %s' % (obj.ref_no, obj.name)

class PlanChoiceField(forms.ModelChoiceField):
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Plan.objects.all().order_by('master_plan__ref_no', 'ref_no')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return unicode('แผน %d - กลุ่มแผนงาน %s %s', 'utf-8') % (obj.master_plan.ref_no, obj.ref_no, obj.name)

# FORM CLASSES

class ModifyPlanForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["master_plan"].queryset = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
	
	master_plan = MasterPlanChoiceField(label='แผนหลัก')
	ref_no = forms.CharField(max_length=512, label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อกลุ่มแผนงาน')

class AddMasterPlanProjectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["plan"].queryset = Plan.objects.filter(master_plan__sector=sector).order_by('master_plan__ref_no', 'ref_no')
	
	plan = PlanChoiceField(label="สังกัดกลุ่มแผนงาน")
	ref_no = forms.CharField(required=False, max_length=64, label='เลขที่แผนงาน')
	name = forms.CharField(max_length=512, label='ชื่อแผนงาน')
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่ม')
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')

class EditMasterPlanProjectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["plan"].queryset = Plan.objects.filter(master_plan__sector=sector).order_by('master_plan__ref_no', 'ref_no')
	
	plan = PlanChoiceField(label="สังกัดกลุ่มแผนงาน")
	ref_no = forms.CharField(required=False, max_length=64, label='เลขที่แผนงาน')
	name = forms.CharField(max_length=512, label='ชื่อแผนงาน')

class ModifyProjectForm(forms.Form):
	ref_no = forms.CharField(required=False, max_length=64, label='เลขที่โครงการ')
	name = forms.CharField(max_length=512, label='ชื่อโครงการ')
	start_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลาโครงการ')
	end_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')

class ActivityForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date      = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่มตั้งแต่วันที่', required=False)
	end_date        = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')

