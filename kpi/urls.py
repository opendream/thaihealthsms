from django.conf.urls.defaults import *

urlpatterns = patterns('kpi.views',
	
	url(r'^sector/(?P<sector_id>\d+)/manage/kpi/$', 'view_sector_manage_kpi', name='view_sector_manage_kpi'),
	url(r'^sector/(?P<sector_id>\d+)/manage/kpi/add/$', 'view_sector_add_kpi', name='view_sector_add_kpi'),
	url(r'^sector/manage/kpi/(?P<kpi_id>\d+)/edit/$', 'view_sector_edit_kpi', name='view_sector_edit_kpi'),
	url(r'^sector/manage/kpi/(?P<kpi_id>\d+)/delete/$', 'view_sector_delete_kpi', name='view_sector_delete_kpi'),
	
	url(r'^sector/manage/project/(?P<project_id>\d+)/edit/kpi/$', 'view_sector_edit_project_kpi', name='view_sector_edit_project_kpi'),
	
	url(r'^master_plan/(?P<master_plan_id>\d+)/kpi/$', 'view_master_plan_kpi', name='view_master_plan_kpi'),
	
	url(r'^project/(?P<project_id>\d+)/kpi/$', 'view_project_kpi', name='view_project_kpi'),
	
	url(r'^kpi/(?P<kpi_schedule_id>\d+)/$', 'view_kpi_overview', name='view_kpi_overview'),
)

urlpatterns += patterns('kpi.ajax',
	url(r'^ajax/kpi/update/$', 'ajax_update_kpi_value', name="ajax_update_kpi_value"),
	
)