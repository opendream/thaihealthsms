# -*- encoding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList

class ChangeFirstTimePasswordForm(forms.Form):
	password1 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่าน')
	password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='ยืนยันรหัสผ่าน')

	def clean(self):
		cleaned_data = self.cleaned_data
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')

		if password1 != password2:
			self._errors["password2"] = ErrorList(['รหัสผ่านไม่สัมพันธ์กัน'])
			del cleaned_data["password2"]

		return cleaned_data

class ChangePasswordForm(forms.Form):
	username = forms.CharField(max_length=500, label='ชื่อผู้ใช้')
	old_password = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่านเก่า')
	new_password1 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='รหัสผ่านใหม่')
	new_password2 = forms.CharField(widget=forms.PasswordInput(), max_length=100, label='ยืนยันรหัสผ่านใหม่')

	def clean(self):
		cleaned_data = self.cleaned_data
		username = cleaned_data.get('username')
		old_password = cleaned_data.get('old_password')
		new_password1 = cleaned_data.get('new_password1')
		new_password2 = cleaned_data.get('new_password2')

		if new_password1 != new_password2:
			self._errors["new_password2"] = ErrorList(['รหัสผ่านไม่สัมพันธ์กัน'])
			del cleaned_data["new_password2"]

		from django.contrib.auth.models import User

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			self._errors["username"] = ErrorList(['ไม่พบผู้ใช้นี้ในระบบ'])
			del cleaned_data["username"]
		else:
			from django.contrib.auth.models import check_password

			if not check_password(old_password, user.password):
				self._errors["old_password"] = ErrorList(['รหัสผ่านไม่ถูกต้อง'])
				del cleaned_data["old_password"]

		return cleaned_data
