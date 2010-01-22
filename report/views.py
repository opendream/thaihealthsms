from datetime import datetime, date

from django.conf import settings
from django.http import HttpResponse, Http404

from report import functions as report_functions
from report.models import *

def notify_overdue_schedule():
	current_date = date.today()
	events = ReportScheduleEvent.objects.filter(due_date=current_date, is_submitted=False)
	
	for event in events:
		
		message_text = "Hey! Today you have due report of %s.\n" % event.schedule.name
		
		from django.core.mail import send_mail
		send_mail('You have overdue report', message_text, 'application.testbed@gmail.com', ['panuta@gmail.com'], fail_silently=False)

def get_nextdue(request):
	report_functions.get_program_nextdue_schedules(1)




def ajax_approve_report_schedule(request):
	if request.method == 'POST':
		report_schedule_id = request.POST['id']
		
		report_schedule = ReportSchedule.objects.get(pk=report_schedule_id)
		report_schedule.state = APPROVE_ACTIVITY
		report_schedule.approval_on = datetime.now()
		report_schedule.save()
		
		return HttpResponse("")
		
	else:
		raise Http404

def ajax_reject_report_schedule(request):
	if request.method == 'POST':
		report_schedule_id = request.POST['id']
		
		report_schedule = ReportSchedule.objects.get(pk=report_schedule_id)
		report_schedule.state = REJECT_ACTIVITY
		report_schedule.approval_on = datetime.now()
		report_schedule.save()
		
		return HttpResponse("")
		
	else:
		raise Http404

def ajax_delete_report_file(request):
	if request.method == 'POST':
		file_id = request.POST['id']
		
		file_response = ReportScheduleFileResponse.objects.get(pk=file_id)
		uploading_directory = "%s/%d/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, file_response.schedule.id, file_response.id)
		
		import os
		os.remove(uploading_directory + file_response.filename)
		
		file_response.delete()

		return HttpResponse("")
		
	else:
		raise Http404
