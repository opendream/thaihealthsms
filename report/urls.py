from django.conf.urls.defaults import *

urlpatterns = patterns('report.views',
	
	url(r'^report/schedule/approve/$', 'ajax_approve_report_schedule', name='ajax_approve_report_schedule'),
	url(r'^report/schedule/reject/$', 'ajax_reject_report_schedule', name='ajax_reject_report_schedule'),
	
	url(r'^report/schedule/file/delete/$', 'ajax_delete_report_file', name='ajax_delete_report_file'),
)
