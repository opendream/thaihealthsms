from django.conf.urls.defaults import *

urlpatterns = patterns('interface.views',
	url(r'^dashboard/$', 'view_dashboard', name="view_dashboard"),
	url(r'^dashboard/projects/$', 'view_dashboard_projects', name="view_dashboard_projects"),
	url(r'^dashboard/comments/$', 'view_dashboard_comments', name="view_dashboard_comments"),
	
	url(r'^administer/$', 'view_administer', name="view_administer"),
	
	# Sector
	url(r'^sector/(?P<sector_id>\d+)/$', 'view_sector_overview', name="view_sector_overview"),
	url(r'^sector/(?P<sector_id>\d+)/master_plans/$', 'view_sector_master_plans', name="view_sector_master_plans"),
	
	url(r'^sectors/$', 'view_sectors_overview', name="view_sectors_overview"),
	
	# Master Plan
	url(r'^master_plan/(?P<master_plan_id>\d+)/$', 'view_master_plan_overview', name="view_master_plan_overview"),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plans/$', 'view_master_plan_plans', name="view_master_plan_plans"),
	
	# Project
	url(r'^program/(?P<program_id>\d+)/$', 'view_program_overview', name="view_program_overview"),
	url(r'^program/(?P<program_id>\d+)/projects/$', 'view_program_projects', name="view_program_projects"),
	url(r'^program/(?P<program_id>\d+)/reports/$', 'view_program_reports', name="view_program_reports"),
	url(r'^program/(?P<program_id>\d+)/reports/send/$', 'view_program_reports_send', name="view_program_reports_send"),
	url(r'^program/(?P<program_id>\d+)/comments/$', 'view_program_comments', name="view_program_comments"),
	
	url(r'^project/(?P<project_id>\d+)/$', 'view_project_overview', name="view_project_overview"),
	url(r'^project/(?P<project_id>\d+)/activities/$', 'view_project_activities', name="view_project_activities"),
	url(r'^project/(?P<project_id>\d+)/reports/$', 'view_project_reports', name="view_project_reports"),
	url(r'^project/(?P<project_id>\d+)/reports/send/$', 'view_project_reports_send', name="view_project_reports_send"),
	url(r'^project/(?P<project_id>\d+)/comments/$', 'view_project_comments', name="view_project_comments"),
	
	url(r'^project/(?P<project_id>\d+)/activities/add/$', 'view_activity_add', name="view_activity_add"),
	
	# Activity
	url(r'^activity/(?P<activity_id>\d+)/$', 'view_activity_overview', name="view_activity_overview"),
	url(r'^activity/(?P<activity_id>\d+)/pictures/$', 'view_activity_pictures', name="view_activity_pictures"),
	url(r'^activity/(?P<activity_id>\d+)/comments/$', 'view_activity_comments', name="view_activity_comments"),
	
	# Report
	url(r'^report/(?P<report_id>\d+)/$', 'view_report_overview', name="view_report_overview"),
	url(r'^report/(?P<report_id>\d+)/comments/$', 'view_report_comments', name="view_report_comments"),
)
