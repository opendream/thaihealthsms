from django.conf.urls.defaults import *

urlpatterns = patterns('comments.views',
	
	url(r'^post-comment/user/(?P<user_id>\d+)/$', 'ajax_post_user_comment', name="ajax_post_user_comment"),
	url(r'^post-comment/object/(?P<object_name>\w+)/(?P<object_id>\d+)/$', 'ajax_post_object_comment', name="ajax_post_object_comment"),
	url(r'^reply-comment/(?P<comment_id>\d+)/$', 'ajax_reply_comment', name="ajax_reply_comment"),
	
	url(r'^query-comment-receivers/$', 'ajax_query_comment_receivers', name="ajax_query_comment_receivers"),
	
	#url(r'^comment/(?P<comment_type>\w+)/(?P<comment_type_id>\d+)/create/$', 'view_comment_save', name="view_comment_save", kwargs={'comment_id': 0}),
	#url(r'^comment/(?P<comment_type>\w+)/(?P<comment_type_id>\d+)/(?P<comment_id>\d+)/edit/$', 'view_comment_save', name="view_comment_save"),
	#url(r'^comment/(?P<comment_type>\w+)/(?P<comment_id>\d+)/delete/$', 'view_comment_delete', name="view_comment_delete"),
)