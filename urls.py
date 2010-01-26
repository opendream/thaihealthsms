import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.static import serve

from django.contrib import admin
admin.autodiscover()

from interface.views import view_frontpage

urlpatterns = patterns('',
	(r'^', include('thaihealthsms.interface.urls')),
	(r'^', include('thaihealthsms.domain.urls')),
	(r'^', include('thaihealthsms.report.urls')),
	(r'^', include('thaihealthsms.comments.urls')),
	
	(r'^accounts/login/', 'thaihealthsms.interface.views.hooked_login'),
	(r'^accounts/first_time/', 'thaihealthsms.interface.views.view_first_time_login'),
	(r'^accounts/change_password/', 'thaihealthsms.interface.views.view_change_password'),
	
	(r'^accounts/', include('registration.backends.default.urls')),
	
	(r'^admin/(.*)', admin.site.root),
	
	(r'^$', view_frontpage),
)

if settings.DEBUG:
    urlpatterns += patterns('', 
        (r'^m/(?P<path>.*)$', serve, {
            'document_root' : os.path.join(os.path.dirname(__file__), "media")
        })
    )