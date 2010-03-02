from django.contrib import admin

from models import *

admin.site.register(Comment)
admin.site.register(CommentReceiverRole)
admin.site.register(CommentReceiver)
admin.site.register(CommentReply)
admin.site.register(CommentReplyReceiver)
