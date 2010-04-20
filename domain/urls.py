from django.conf.urls.defaults import *

urlpatterns = patterns('domain.views',

	# Sector
	url(r'^sectors/$', 'view_sectors', name='view_sectors'),
	url(r'^sector/(?P<sector_id>\d+)/$', 'view_sector_overview', name='view_sector_overview'),
	url(r'^sector/(?P<sector_id>\d+)/manage/organization/$', 'view_sector_manage_organization', name='view_sector_manage_organization'),
	
	url(r'^sector/(?P<sector_id>\d+)/manage/plan/add/$', 'view_sector_add_plan', name='view_sector_add_plan'),
	url(r'^sector/manage/plan/(?P<plan_id>\d+)/edit/$', 'view_sector_edit_plan', name='view_sector_edit_plan'),
	url(r'^sector/manage/plan/(?P<plan_id>\d+)/delete/$', 'view_sector_delete_plan', name='view_sector_delete_plan'),
	
	url(r'^sector/(?P<sector_id>\d+)/manage/project/add/$', 'view_sector_add_project', name='view_sector_add_project'),
	url(r'^sector/manage/project/(?P<project_id>\d+)/edit/$', 'view_sector_edit_project', name='view_sector_edit_project'),
	
	url(r'^sector/manage/project/(?P<project_id>\d+)/delete/$', 'view_sector_delete_project', name='view_sector_delete_project'),
	
	# Master Plan
	url(r'^master_plan/(?P<master_plan_id>\d+)/$', 'view_master_plan_overview', name='view_master_plan_overview'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/plans/$', 'view_master_plan_plans', name='view_master_plan_plans'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/organization/$', 'view_master_plan_organization', name='view_master_plan_organization'),
	url(r'^master_plan/(?P<master_plan_id>\d+)/report/$', 'view_master_plan_report', name='view_master_plan_report'),
	
	# Project
	url(r'^project/(?P<project_id>\d+)/$', 'view_project_overview', name='view_project_overview'),
	url(r'^project/(?P<project_id>\d+)/projects/$', 'view_project_projects', name='view_project_projects'),
	url(r'^project/(?P<project_id>\d+)/projects/add/$', 'view_project_add', name='view_project_add'),
	url(r'^project/(?P<project_id>\d+)/delete/$', 'view_project_delete', name='view_project_delete'),
	url(r'^project/(?P<project_id>\d+)/edit/$', 'view_project_edit', name='view_project_edit'),
	url(r'^project/(?P<project_id>\d+)/activities/$', 'view_project_activities', name='view_project_activities'),
	url(r'^project/(?P<project_id>\d+)/activities/add/$', 'view_activity_add', name='view_activity_add'),

	# Activity
	url(r'^activity/(?P<activity_id>\d+)/$', 'view_activity_overview', name="view_activity_overview"),
	url(r'^activity/(?P<activity_id>\d+)/edit/$', 'view_activity_edit', name="view_activity_edit"),
	url(r'^activity/(?P<activity_id>\d+)/delete/$', 'view_activity_delete', name="view_activity_delete"),
)

urlpatterns += patterns('domain.ajax',
	url(r'^ajax/list/master_plans/$', 'ajax_list_master_plans', name='ajax_list_master_plans'),
	url(r'^ajax/list/projects/$', 'ajax_list_projects', name='ajax_list_projects'),
	url(r'^ajax/list/project/activities/$', 'ajax_list_project_activities', name='ajax_list_project_activities'),
)
