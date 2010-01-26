from django.conf.urls.defaults import *
from interface.forms import *

urlpatterns = patterns('interface.views',
	url(r'^/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/comments/$', 'view_dashboard_comments', name='view_dashboard_comments'),
	url(r'^dashboard/comments/outbox/$', 'view_dashboard_comments_outbox', name='view_dashboard_comments_outbox'),
	url(r'^dashboard/my_projects/$', 'view_dashboard_my_projects', name='view_dashboard_my_projects'),
	
	url(r'^administer/$', 'view_administer', name='view_administer'),
	url(r'^administer/organization/$', 'view_administer_organization', name='view_administer_organization'),
	url(r'^administer/organization/sector/add/$', 'view_administer_organization_add_sector', name='view_administer_organization_add_sector'),
	url(r'^administer/organization/sector/(?P<sector_id>\d+)/edit/$', 'view_administer_organization_edit_sector', name='view_administer_organization_edit_sector'),
	url(r'^administer/organization/sector/(?P<sector_id>\d+)/delete/$', 'view_administer_organization_delete_sector', name='view_administer_organization_delete_sector'),
	url(r'^administer/organization/masterplan/add/$', 'view_administer_organization_add_masterplan', name='view_administer_organization_add_masterplan'),
	url(r'^administer/organization/masterplan/(?P<master_plan_id>\d+)/edit/$', 'view_administer_organization_edit_masterplan', name='view_administer_organization_edit_masterplan'),
	url(r'^administer/organization/masterplan/(?P<master_plan_id>\d+)/delete/$', 'view_administer_organization_delete_masterplan', name='view_administer_organization_delete_masterplan'),
	
	url(r'^administer/users/$', 'view_administer_users', name='view_administer_users'),
	url(r'^administer/users/add/$', 'view_administer_users_add', name='view_administer_users_add'),
	url(r'^administer/users/(?P<user_id>\d+)/edit/$', 'view_administer_users_edit', name='view_administer_users_edit'),
	url(r'^administer/users/(?P<user_id>\d+)/password/$', 'view_administer_users_password', name='view_administer_users_password'),
	url(r'^administer/users/(?P<user_id>\d+)/status/$', 'view_administer_users_status', name="view_administer_users_status"),	
	
	# Sector
	url(r'^sector/(?P<sector_id>\d+)/$', 'view_sector_overview', name='view_sector_overview'),
	url(r'^sector/(?P<sector_id>\d+)/reports/$', 'view_sector_reports', name='view_sector_reports'),
	url(r'^sector/(?P<sector_id>\d+)/reports/add/$', 'view_sector_add_report', name='view_sector_add_report'),
	url(r'^sector/(?P<sector_id>\d+)/report/(?P<report_id>\d+)/edit/$', 'view_sector_edit_report', name='view_sector_edit_report'),
	url(r'^sector/(?P<sector_id>\d+)/report/(?P<report_id>\d+)/delete/$', 'view_sector_delete_report', name='view_sector_delete_report'),
	url(r'^sectors/$', 'view_sectors', name='view_sectors'),
	
	# Master Plan
	url(r'^master_plan/(?P<master_plan_id>\d+)/$', 'view_master_plan_overview', name='view_master_plan_overview'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plans/$', 'view_master_plan_plans', name='view_master_plan_plans'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/organization/$', 'view_master_plan_organization', name='view_master_plan_organization'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plans/add/$', 'view_master_plan_add_plan', name='view_master_plan_add_plan'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plan/(?P<plan_id>\d+)/$', 'view_master_plan_edit_plan', name='view_master_plan_edit_plan'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plan/(?P<plan_id>\d+)/delete/$', 'view_master_plan_delete_plan', name='view_master_plan_delete_plan'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/projects/add/$', 'view_master_plan_add_project', name='view_master_plan_add_project'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plan/(?P<project_id>\d+)/$', 'view_master_plan_edit_project', name='view_master_plan_edit_project'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plan/(?P<project_id>\d+)/delete/$', 'view_master_plan_delete_project', name='view_master_plan_delete_project'),
	
	url(r'^project/(?P<project_id>\d+)/$', 'view_project_overview', name='view_project_overview'),
	url(r'^project/(?P<project_id>\d+)/projects/$', 'view_project_projects', name='view_project_projects'),
	url(r'^project/(?P<project_id>\d+)/projects/add/$', 'view_project_add', name='view_project_add'),
	url(r'^project/(?P<project_id>\d+)/delete/$', 'view_project_delete', name='view_project_delete'),
	url(r'^project/(?P<project_id>\d+)/edit/$', 'view_project_edit', name='view_project_edit'),
	url(r'^project/(?P<project_id>\d+)/reports/$', 'view_project_reports', name='view_project_reports'),
	url(r'^project/(?P<project_id>\d+)/reports/list/$', 'view_project_reports_list', name='view_project_reports_list'),
	url(r'^project/(?P<project_id>\d+)/reports/add/$', 'view_project_reports_add', name='view_project_reports_add'),
	url(r'^project/(?P<project_id>\d+)/report/(?P<report_id>\d+)/edit/$', 'view_project_report_edit', name='view_project_report_edit'),
	url(r'^project/(?P<project_id>\d+)/reports/send/$', 'view_project_reports_send', name='view_project_reports_send'),
	url(r'^project/(?P<project_id>\d+)/activities/$', 'view_project_activities', name='view_project_activities'),
	url(r'^project/(?P<project_id>\d+)/activities/(?P<yearmonth>\d{4}\d{2})$', 'view_project_activities_ajax', name="view_project_activities_ajax"),
	url(r'^project/(?P<project_id>\d+)/activities/add/$', 'view_activity_add', name='view_activity_add'),
	url(r'^project/(?P<project_id>\d+)/comments/$', 'view_project_comments', name='view_project_comments'),


	# Activity
	url(r'^activity/(?P<activity_id>\d+)/$', 'view_activity_overview', name="view_activity_overview"),
	url(r'^activity/(?P<activity_id>\d+)/edit/$', 'view_activity_edit', name="view_activity_edit"),
	url(r'^activity/(?P<activity_id>\d+)/delete/$', 'view_activity_delete', name="view_activity_delete"),
	url(r'^activity/(?P<activity_id>\d+)/comments/$', 'view_activity_comments', name="view_activity_comments"),

	# Report
	url(r'^report/(?P<report_id>\d+)/$', 'view_report_overview', name='view_report_overview'),
	url(r'^report/(?P<report_id>\d+)/comments/$', 'view_report_comments', name='view_report_comments'),
)


#urlpatterns += patterns('',
#	url(r'^administer/users/add/$', UserAccountWizard([UserAccountFormStart, UserAccountFormSecond]), name="view_administer_users_add"),
#	url(r'^administer/users/(?P<user_id>\d+)/edit/$', UserAccountWizard([UserAccountFormStart, UserAccountFormSecond]), name="view_administer_users_edit"),
#	
#)
