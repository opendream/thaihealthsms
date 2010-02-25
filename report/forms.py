# -*- encoding: utf-8 -*-
from django import forms

from widgets import YUICalendar

from models import Report

month_cycle = [(i,i) for i in range(1,13)]
date_cycle = [(0, 'วันสิ้นเดือน'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12),(13,13),(14,14),(15,15),(16,16),(17,17),(18,18),(19,19),(20,20),(21,21),(22,22),(23,23),(24,24),(25,25),(26,26),(27,27),(28,28),(29,29),(30,30),(31,31)]

# FIELD CLASSES

class ReportChoiceField(forms.ModelMultipleChoiceField):
	widget = forms.CheckboxSelectMultiple
	
	def __init__(self, *args, **kwargs):
		kwargs['empty_label'] = None
		kwargs['queryset'] = Report.objects.all().order_by('name')
		forms.ModelChoiceField.__init__(self, *args, **kwargs)
	
	def label_from_instance(self, obj):
		return obj.name

# FORM CLASSES

class SectorReportForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อรายงาน')
	need_approval = forms.BooleanField(required=False, label='รายงานที่ส่งมา ต้องมีการรับรองรายงาน')
	schedule_cycle_length = forms.ChoiceField(choices=month_cycle)
	start_now = forms.BooleanField(required=False, label='เริ่มส่งรายงานในเดือนปัจจุบัน (ถ้าไม่เลือก หมายถึงเริ่มส่งรายงานในเดือนถัดไป)')
	schedule_monthly_date = forms.ChoiceField(choices=date_cycle)
	notify_days = forms.IntegerField(label='แจ้งเตือนก่อนถึงวันส่งรายงานล่วงหน้า', required=False)

class ProjectReportForm(forms.Form):
	name = forms.CharField(max_length=512, label='ชื่อรายงาน')
	need_checkup = forms.BooleanField(required=False, label='ส่งรายงานถึงผู้ประสานงานสำนัก')
	need_approval = forms.BooleanField(required=False, label='ต้องรับรองรายงาน')
	schedule_cycle_length = forms.ChoiceField(choices=month_cycle)
	start_now = forms.BooleanField(required=False, label='เริ่มส่งรายงานในเดือนปัจจุบัน (ถ้าไม่เลือก หมายถึงเริ่มส่งรายงานในเดือนถัดไป)')
	schedule_monthly_date = forms.ChoiceField(choices=date_cycle)
	notify_days = forms.IntegerField(label='แจ้งเตือนก่อนถึงวันส่งรายงานล่วงหน้า', required=False)

class MasterPlanProjectReportsForm(forms.Form):
	def __init__(self, *args, **kwargs):
		sector = kwargs.pop('sector', None)
		forms.Form.__init__(self, *args, **kwargs)
		
		if sector:
			self.fields["reports"].queryset = Report.objects.filter(sector=sector).order_by('name')
	
	reports = ReportChoiceField(label='รายงาน')
