from django.db import models
from django.contrib.auth.models import Group

class Comment(models.Model):
	message = models.CharField(max_length=1024)
	object_id = models.IntegerField(default=0)
	object_name = models.CharField(max_length=64, null=True)
	is_private = models.BooleanField(default=True)
	is_urgent = models.BooleanField(default=False)
	sent_on = models.DateTimeField(auto_now_add=True)
	sent_by = models.ForeignKey('domain.UserAccount')

class CommentReceiverRole(models.Model):
	object_name = models.CharField(max_length=64)
	role = models.ForeignKey(Group)

class CommentReceiver(models.Model):
	comment = models.ForeignKey('Comment')
	receiver = models.ForeignKey('domain.UserAccount')
	is_read = models.BooleanField(default=False)
	sent_on = models.DateTimeField() # Save value as in Comment

class CommentReply(models.Model):
	comment = models.ForeignKey('Comment')
	content = models.CharField(max_length=1024)
	sent_on = models.DateTimeField(auto_now_add=True)
	sent_by = models.ForeignKey('domain.UserAccount')

	class Meta:
		ordering = ['sent_on']
