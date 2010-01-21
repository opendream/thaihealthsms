from django.conf.urls.defaults import *
from interface.forms import *

urlpatterns = patterns('interface.views',
	url(r'^/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/comments/$', 'view_dashboard_comments', name='view_dashboard_comments'),

	url(r'^administer/$', 'view_administer', name='view_administer'),
	url(r'^administer/organization/$', 'view_administer_organization', name='view_administer_organization'),
	url(r'^administer/users/$', 'view_administer_users', name='view_administer_users'),
	url(r'^administer/users/add/$', 'view_administer_users_add', name='view_administer_users_add'),
	url(r'^administer/users/(?P<sector_id>\d+)/programs/$', 'view_administer_users_programs', name='view_administer_users_programs'),
	url(r'^administer/users/(?P<sector_id>\d+)/projects/$', 'view_administer_users_projects', name='view_administer_users_projects'),

	# Sector
	url(r'^sector/(?P<sector_id>\d+)/$', 'view_sector_overview', name='view_sector_overview'),
	url(r'^sector/(?P<sector_id>\d+)/kpi/$', 'view_sector_kpi', name='view_sector_kpi'),

	url(r'^sectors/$', 'view_sectors_overview', name='view_sectors_overview'),

	# Master Plan
	url(r'^master_plan/(?P<master_plan_id>\d+)/$', 'view_master_plan_overview', name='view_master_plan_overview'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plans/$', 'view_master_plan_plans', name='view_master_plan_plans'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/kpi/$', 'view_master_plan_kpi', name='view_master_plan_kpi'),

	# Project
	url(r'^program/(?P<program_id>\d+)/$', 'view_program_overview', name='view_program_overview'),
	url(r'^program/(?P<program_id>\d+)/projects/$', 'view_program_projects', name='view_program_projects'),
	url(r'^program/(?P<program_id>\d+)/reports/$', 'view_program_reports', name='view_program_reports'),
	url(r'^program/(?P<program_id>\d+)/reports/send/$', 'view_program_reports_send', name='view_program_reports_send'),
	url(r'^program/(?P<program_id>\d+)/kpi/$', 'view_program_kpi', name='view_program_kpi'),
	url(r'^program/(?P<program_id>\d+)/finance/$', 'view_program_finance', name='view_program_finance'),
	url(r'^program/(?P<program_id>\d+)/comments/$', 'view_program_comments', name='view_program_comments'),

	url(r'^project/(?P<project_id>\d+)/$', 'view_project_overview', name='view_project_overview'),
	url(r'^project/(?P<project_id>\d+)/activities/$', 'view_project_activities', name='view_project_activities'),
	url(r'^project/(?P<project_id>\d+)/activities/(?P<yearmonth>\d{4}\d{2})$', 'view_project_activities_ajax', name="view_project_activities_ajax"),
	url(r'^project/(?P<project_id>\d+)/reports/$', 'view_project_reports', name='view_project_reports'),
	url(r'^project/(?P<project_id>\d+)/reports/send/$', 'view_project_reports_send', name='view_project_reports_send'),
	url(r'^project/(?P<project_id>\d+)/comments/$', 'view_project_comments', name='view_project_comments'),

	url(r'^project/(?P<project_id>\d+)/activities/add/$', 'view_activity_add', name='view_activity_add'),

	# Activity
	url(r'^activity/(?P<activity_id>\d+)/$', 'view_activity_overview', name="view_activity_overview"),
	url(r'^activity/(?P<activity_id>\d+)/edit/$', 'view_activity_edit', name="view_activity_edit"),
	url(r'^activity/(?P<activity_id>\d+)/delete/$', 'view_activity_delete', name="view_activity_delete"),
	url(r'^activity/(?P<activity_id>\d+)/pictures/$', 'view_activity_pictures', name="view_activity_pictures"),
	url(r'^activity/(?P<activity_id>\d+)/comments/$', 'view_activity_comments', name="view_activity_comments"),

	# Report
	url(r'^report/(?P<report_id>\d+)/$', 'view_report_overview', name='view_report_overview'),
	url(r'^report/(?P<report_id>\d+)/comments/$', 'view_report_comments', name='view_report_comments'),
)
