from domain.models import UserAccount

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)


