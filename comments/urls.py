from django.conf.urls.defaults import *

urlpatterns = patterns('comments.views',
	url(r'^dashboard/comments/$', 'view_dashboard_comments', name='view_dashboard_comments'),
					
	url(r'^project/(?P<project_id>\d+)/comments/$', 'view_project_comments', name='view_project_comments'),
	url(r'^activity/(?P<activity_id>\d+)/comments/$', 'view_activity_comments', name="view_activity_comments"),
	url(r'^report/(?P<report_id>\d+)/comments/$', 'view_report_comments', name='view_report_comments'),
)

urlpatterns += patterns('comments.ajax',
	url(r'^ajax/comment/post/(?P<object_name>\w+)/(?P<object_id>\d+)/$', 'ajax_post_object_comment', name="ajax_post_object_comment"),
	url(r'^ajax/comment/reply/(?P<comment_id>\d+)/$', 'ajax_reply_comment', name="ajax_reply_comment"),
)