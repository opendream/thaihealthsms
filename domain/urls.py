from django.conf.urls.defaults import *

urlpatterns = patterns('domain.views',
	
	url(r'^ajax/list/master_plans/$', 'ajax_list_master_plans', name='ajax_list_master_plans'),
	url(r'^ajax/list/projects/$', 'ajax_list_projects', name='ajax_list_projects'),
	
	
)