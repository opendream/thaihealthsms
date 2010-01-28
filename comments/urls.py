from django.conf.urls.defaults import *

urlpatterns = patterns('comments.views',
	
	url(r'^post-comment/(?P<object_name>\w+)/(?P<object_id>\d+)/$', 'ajax_post_object_comment', name="ajax_post_object_comment"),
	url(r'^reply-comment/(?P<comment_id>\d+)/$', 'ajax_reply_comment', name="ajax_reply_comment"),
	
)
