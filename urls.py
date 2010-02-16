import os

from django.conf.urls.defaults import *
from django.conf import settings
from django.views.static import serve

from django.contrib import admin
admin.autodiscover()

from dashboard.views import view_frontpage

urlpatterns = patterns('',
	(r'^', include('thaihealthsms.accounts.urls')),
	(r'^', include('thaihealthsms.administer.urls')),
	(r'^', include('thaihealthsms.comments.urls')),
	(r'^', include('thaihealthsms.dashboard.urls')),
	(r'^', include('thaihealthsms.domain.urls')),
	(r'^', include('thaihealthsms.finance.urls')),
	(r'^', include('thaihealthsms.kpi.urls')),
	(r'^', include('thaihealthsms.report.urls')),
	
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