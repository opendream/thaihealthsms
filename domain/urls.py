from django.conf.urls.defaults import *

urlpatterns = patterns('domain.views',
	
	url(r'^ajax/update-kpi-submission/$', 'ajax_update_kpi_submission', name="ajax_update_kpi_submission"),
	url(r'^ajax/update-finance-kpi-submission/$', 'ajax_update_finance_kpi_submission', name="ajax_update_finance_kpi_submission"),
	
)