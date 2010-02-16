# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import simplejson

from accounts.forms import *
from accounts.models import *

from helper.shortcuts import render_response

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)

from django.contrib.auth.views import login
from django.contrib.auth import REDIRECT_FIELD_NAME

def hooked_login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
	response = login(request, template_name, redirect_field_name)

	if request.user.is_authenticated():
		if not request.user.is_superuser and request.user.get_profile().random_password:
			return redirect('/accounts/first_time/')

	return response

@login_required
def view_first_time_login(request):
	if request.user.is_authenticated():
		if request.user.is_superuser or (not request.user.is_superuser and not request.user.get_profile().random_password):
			return redirect('/')

	if request.method == 'POST':
		form = ChangeFirstTimePasswordForm(request.POST)
		if form.is_valid():
			password1 = form.cleaned_data['password1']
			password2 =form.cleaned_data['password2']

			user = request.user
			user.set_password(password1)
			user.save()

			user_account = user.get_profile()
			user_account.random_password = ''
			user_account.save()

			next = request.POST.get('next')
			if not next: next = '/'
			return redirect(next)

	else:
		form = ChangeFirstTimePasswordForm()

	next = request.GET.get('next', '')
	return render_response(request, "registration/first_time_login.html", {'form':form, 'next':next})

def view_change_password(request):
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			old_password = form.cleaned_data['old_password']
			new_password1 = form.cleaned_data['new_password1']
			new_password2 =form.cleaned_data['new_password2']

			user = User.objects.get(username=username)
			user.set_password(new_password1)
			user.save()

			return redirect('/accounts/login/')

	else:
		form = ChangePasswordForm()

	return render_response(request, "registration/change_password.html", {'form':form,})
