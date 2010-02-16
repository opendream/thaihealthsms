from django.conf.urls.defaults import *

urlpatterns = patterns('accounts.views',
	(r'^accounts/login/', 'hooked_login'),
	(r'^accounts/first_time/', 'view_first_time_login'),
	(r'^accounts/change_password/', 'view_change_password'),	
)