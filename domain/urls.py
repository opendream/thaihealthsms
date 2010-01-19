from django.conf.urls.defaults import *

urlpatterns = patterns('domain.views',
	
	url(r'^ajax/update-kpi-schedule/$', 'ajax_update_kpi_schedule', name="ajax_update_kpi_schedule"),
	url(r'^ajax/update-finance-schedule/$', 'ajax_update_finance_schedule', name="ajax_update_finance_schedule"),
	
)