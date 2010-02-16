from django.conf.urls.defaults import *

urlpatterns = patterns('report.views',
	
	# Sector
	url(r'^sector/(?P<sector_id>\d+)/manage/reports/$', 'view_sector_manage_reports', name='view_sector_manage_reports'),
	
	url(r'^sector/(?P<sector_id>\d+)/manage/report/add/$', 'view_sector_add_report', name='view_sector_add_report'),
	url(r'^sector/manage/report/(?P<report_id>\d+)/edit/$', 'view_sector_edit_report', name='view_sector_edit_report'),
	url(r'^sector/manage/report/(?P<report_id>\d+)/delete/$', 'view_sector_delete_report', name='view_sector_delete_report'),
	
	url(r'^sector/manage/project/(?P<project_id>\d+)/edit/reports/$', 'view_sector_edit_project_reports', name='view_sector_edit_project_reports'),
	
	# Project
	url(r'^project/(?P<project_id>\d+)/reports/$', 'view_project_reports', name='view_project_reports'),
	url(r'^project/(?P<project_id>\d+)/reports/manage/$', 'view_project_reports_manage', name='view_project_reports_manage'),
	url(r'^project/(?P<project_id>\d+)/reports/add/$', 'view_project_reports_add', name='view_project_reports_add'),
	url(r'^project/(?P<project_id>\d+)/report/(?P<report_id>\d+)/edit/$', 'view_project_report_edit', name='view_project_report_edit'),
	url(r'^project/(?P<project_id>\d+)/reports/send/$', 'view_project_reports_send', name='view_project_reports_send'),

	# Report
	url(r'^report/(?P<report_id>\d+)/$', 'view_report_overview', name='view_report_overview'),
)

urlpatterns += patterns('report.ajax',
	url(r'^ajax/report/schedule/approve/$', 'ajax_approve_report_schedule', name='ajax_approve_report_schedule'),
	url(r'^ajax/report/schedule/reject/$', 'ajax_reject_report_schedule', name='ajax_reject_report_schedule'),
	url(r'^ajax/report/schedule/file/delete/$', 'ajax_delete_report_file', name='ajax_delete_report_file'),
)