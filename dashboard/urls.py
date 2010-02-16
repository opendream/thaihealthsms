from django.conf.urls.defaults import *

urlpatterns = patterns('dashboard.views',
	url(r'^/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/$', 'view_frontpage', name='view_frontpage'),
	url(r'^dashboard/my_projects/$', 'view_dashboard_my_projects', name='view_dashboard_my_projects'),
)