# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

from report.forms import ReportChoiceField

from domain.models import Sector, MasterPlan, Plan, Project, Activity
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
		
		self.fields["master_plan"].queryset = MasterPlan.objects.filter(sector=sector).order_by('ref_no')
		self.sector = sector
	
	plan_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	master_plan = MasterPlanChoiceField(label='แผนหลัก')
	ref_no = forms.CharField(max_length=512, label='รหัส')
	name = forms.CharField(max_length=512, label='ชื่อกลุ่มแผนงาน')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		plan_id = cleaned_data.get('plan_id')
		ref_no = cleaned_data.get('ref_no')
		
		if plan_id: existing = Plan.objects.filter(ref_no=ref_no, master_plan__sector=self.sector).exclude(id=plan_id).count()
		else: existing = Plan.objects.filter(ref_no=ref_no, master_plan__sector=self.sector).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขที่กลุ่มแผนงานนี้ซ้ำกับกลุ่มแผนงานอื่นในสำนัก'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class AddMasterPlanProjectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["plan"].queryset = Plan.objects.filter(master_plan__sector=sector).order_by('master_plan__ref_no', 'ref_no')
			self.sector = sector
	
	plan = PlanChoiceField(label="กลุ่มแผนงาน")
	ref_no = forms.CharField(max_length=64, label='เลขที่แผนงาน')
	name = forms.CharField(max_length=512, label='ชื่อแผนงาน')
	start_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลา', required=False)
	end_date = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		ref_no = cleaned_data.get('ref_no')
		
		existing = Project.objects.filter(ref_no=ref_no, parent_project=None, master_plan__sector=self.sector).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขที่แผนงานนี้ซ้ำกับแผนงานอื่นในสำนัก'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class EditMasterPlanProjectForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["plan"].queryset = Plan.objects.filter(master_plan__sector=sector).order_by('master_plan__ref_no', 'ref_no')
	
	plan = PlanChoiceField(label="กลุ่มแผนงาน")
	ref_no = forms.CharField(max_length=64, label='เลขที่แผนงาน')
	name = forms.CharField(max_length=512, label='ชื่อแผนงาน')

class ModifyProjectForm(forms.Form):
	parent_project_id = forms.IntegerField(widget=forms.HiddenInput())
	project_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
	ref_no = forms.CharField(required=False, max_length=64, label='เลขที่โครงการ')
	name = forms.CharField(max_length=512, label='ชื่อโครงการ')
	start_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_start_date'}), label='ระยะเวลาโครงการ')
	end_date = forms.DateField(required=False, widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		parent_project_id = cleaned_data.get('parent_project_id')
		project_id = cleaned_data.get('project_id')
		ref_no = cleaned_data.get('ref_no')
		
		parent_project = Project.objects.get(pk=parent_project_id)
		
		if project_id: existing = Project.objects.filter(ref_no=ref_no, parent_project=parent_project).exclude(parent_project=None, id=project_id).count()
		else: existing = Project.objects.filter(ref_no=ref_no, parent_project=parent_project).exclude(parent_project=None).count()
		
		if existing:
			self._errors['ref_no'] = ErrorList(['เลขที่โครงการนี้ซ้ำกับโครงการอื่นในแผนงาน'])
			del cleaned_data['ref_no']
		
		return cleaned_data

class ActivityForm(forms.Form):
	name 			= forms.CharField(max_length=500, label='ชื่อกิจกรรม')
	start_date      = forms.DateField(widget=YUICalendar(attrs={'id':'id_start_date'}), label='เริ่มตั้งแต่วันที่', required=False)
	end_date        = forms.DateField(widget=YUICalendar(attrs={'id':'id_end_date'}), label='ถึง', required=False)
	description 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='รายละเอียด')
	location 		= forms.CharField(max_length=2000, required=False, label='สถานที่')
	result_goal 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่ต้องการ')
	result_real 	= forms.CharField(max_length=2000, required=False, widget=forms.Textarea(), label='ผลลัพธ์ที่เกิดขึ้น')
	
	def clean(self):
		cleaned_data = self.cleaned_data
		start_date = cleaned_data.get('start_date')
		end_date = cleaned_data.get('end_date')
		
		if start_date > end_date:
			self._errors['start_date'] = ErrorList(['วันที่เริ่มต้นเกิดขึ้นหลังจากวันที่สิ้นสุด'])
			del cleaned_data['start_date']
		
		return cleaned_data

