

def user_account(request):
	"""
	Return UserAccount object if user is authenticated
	"""
	if request.user.is_authenticated():
		from domain.models import UserAccount
		user_account = UserAccount.objects.get(user=request.user)
	else:
		user_account = None
	
	return {'user_account': user_account}