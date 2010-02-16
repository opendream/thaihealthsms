from django.conf.urls.defaults import *

urlpatterns = patterns('finance.views',
	url(r'^sector/manage/project/(?P<project_id>\d+)/edit/finance/$', 'view_sector_edit_project_finance', name='view_sector_edit_project_finance'),
	
	url(r'^project/(?P<project_id>\d+)/finance/$', 'view_project_finance', name='view_project_finance'),
	
	url(r'^finance/(?P<finance_schedule_id>\d+)/$', 'view_finance_overview', name='view_finance_overview'),
	
)

urlpatterns += patterns('finance.ajax',
	url(r'^ajax/finance/update/$', 'ajax_update_finance_value', name="ajax_update_finance_value"),
	url(r'^ajax/finance/claim/$', 'ajax_claim_finance_schedule', name="ajax_claim_finance_schedule"),
)