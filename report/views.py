from datetime import date

from report import functions as report_functions

def notify_overdue_schedule():
	current_date = date.today()
	events = ReportScheduleEvent.objects.filter(due_date=current_date, is_submitted=False)
	
	for event in events:
		
		message_text = "Hey! Today you have due report of %s.\n" % event.schedule.name
		
		from django.core.mail import send_mail
		send_mail('You have overdue report', message_text, 'application.testbed@gmail.com', ['panuta@gmail.com'], fail_silently=False)

def get_nextdue(request):
	report_functions.get_program_nextdue_schedules(1)
	