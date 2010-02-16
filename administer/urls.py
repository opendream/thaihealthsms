from django.conf.urls.defaults import *

urlpatterns = patterns('administer.views',
	url(r'^administer/$', 'view_administer', name='view_administer'),
	
	# Organization
	url(r'^administer/organization/$', 'view_administer_organization', name='view_administer_organization'),
	url(r'^administer/organization/sector/add/$', 'view_administer_organization_add_sector', name='view_administer_organization_add_sector'),
	url(r'^administer/organization/sector/(?P<sector_id>\d+)/edit/$', 'view_administer_organization_edit_sector', name='view_administer_organization_edit_sector'),
	url(r'^administer/organization/sector/(?P<sector_id>\d+)/delete/$', 'view_administer_organization_delete_sector', name='view_administer_organization_delete_sector'),
	url(r'^administer/organization/masterplan/add/$', 'view_administer_organization_add_masterplan', name='view_administer_organization_add_masterplan'),
	url(r'^administer/organization/masterplan/(?P<master_plan_id>\d+)/edit/$', 'view_administer_organization_edit_masterplan', name='view_administer_organization_edit_masterplan'),
	url(r'^administer/organization/masterplan/(?P<master_plan_id>\d+)/delete/$', 'view_administer_organization_delete_masterplan', name='view_administer_organization_delete_masterplan'),
	
	# Users
	url(r'^administer/users/$', 'view_administer_users', name='view_administer_users'),
	url(r'^administer/user/add/$', 'view_administer_users_add', name='view_administer_users_add'),
	url(r'^administer/user/(?P<user_id>\d+)/edit/$', 'view_administer_users_edit', name='view_administer_users_edit'),
	url(r'^administer/user/(?P<user_id>\d+)/password/$', 'view_administer_users_password', name='view_administer_users_password'),
	
	# KPI
	url(r'^administer/kpi/$', 'view_administer_kpi', name='view_administer_kpi'),
	url(r'^administer/kpi-category/$', 'view_administer_kpi_category', name='view_administer_kpi_category'),
	
	url(r'^administer/kpi/add/$', 'view_administer_kpi_add', name='view_administer_kpi_add'),
	url(r'^administer/kpi/(?P<kpi_id>\d+)/edit/$', 'view_administer_kpi_edit', name='view_administer_kpi_edit'),
	url(r'^administer/kpi/(?P<kpi_id>\d+)/delete/$', 'view_administer_kpi_delete', name='view_administer_kpi_delete'),
	
	url(r'^administer/kpi-category/add/$', 'view_administer_kpi_category_add', name='view_administer_kpi_category_add'),
	url(r'^administer/kpi-category/(?P<category_id>\d+)/edit/$', 'view_administer_kpi_category_edit', name='view_administer_kpi_category_edit'),
	url(r'^administer/kpi-category/(?P<category_id>\d+)/delete/$', 'view_administer_kpi_category_delete', name='view_administer_kpi_category_delete'),
)