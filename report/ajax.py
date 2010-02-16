from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils import simplejson

from models import *

from helper.utilities import format_abbr_datetime

def ajax_approve_report_schedule(request):
	if request.method == 'POST':
		report_schedule_id = request.POST['id']
		
		report_schedule = ReportSchedule.objects.get(pk=report_schedule_id)
		report_schedule.state = APPROVE_ACTIVITY
		report_schedule.approval_on = datetime.now()
		report_schedule.save()
		
		return HttpResponse(simplejson.dumps({'timestamp':format_abbr_datetime(report_schedule.approval_on)}))
		
	else:
		raise Http404

def ajax_reject_report_schedule(request):
	if request.method == 'POST':
		report_schedule_id = request.POST['id']
		
		report_schedule = ReportSchedule.objects.get(pk=report_schedule_id)
		report_schedule.state = REJECT_ACTIVITY
		report_schedule.approval_on = datetime.now()
		report_schedule.save()
		
		return HttpResponse(simplejson.dumps({'timestamp':format_abbr_datetime(report_schedule.approval_on)}))
		
	else:
		raise Http404

def ajax_delete_report_file(request):
	if request.method == 'POST':
		file_id = request.POST['id']
		
		file_response = ReportScheduleFileResponse.objects.get(pk=file_id)
		uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, file_response.schedule.report_project.report.id, file_response.schedule.id)
		
		import os
		os.remove(uploading_directory + file_response.filename)
		
		file_response.delete()

		return HttpResponse("")
		
	else:
		raise Http404
