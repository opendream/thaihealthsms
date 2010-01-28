# -*- encoding: utf-8 -*-

import calendar
from datetime import datetime, date
import os

from django.db.models import Q
from django.db.models import F

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.core import serializers
from django.utils import simplejson

from thaihealthsms.shortcuts import render_response, access_denied

from comments.models import *
from domain.models import *
from report.models import *

from interface.forms import *

from comments import functions as comments_functions
from domain import functions as domain_functions
from report import functions as report_functions
from helper import utilities

def view_frontpage(request):
	if request.user.is_authenticated(): return view_dashboard(request)
	else: return redirect("/accounts/login/")

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

#
# FRONTPAGE
#
@login_required
def view_frontpage(request):
	if request.user.is_superuser:
		return _view_admin_frontpage(request)

	else:
		primary_role = request.user.groups.all()[0] # Currently support only 1 role per user

		if primary_role.name == "sector_admin":
			return _view_sector_admin_frontpage(request)

		elif primary_role.name == "sector_manager":
			return _view_sector_manager_frontpage(request)

		elif primary_role.name == "sector_manager_assistant":
			return _view_sector_manager_assistant_frontpage(request)

		elif primary_role.name == "project_manager":
			return _view_project_manager_frontpage(request)

		elif primary_role.name == "project_manager_assistant":
			return _view_project_manager_assistant_frontpage(request)

def _view_admin_frontpage(request):
	return redirect("/administer/")

def _view_sector_admin_frontpage(request):
	return redirect("/sector/%d/" % request.user.get_profile().sector.id)

def _view_sector_manager_frontpage(request):
	return redirect("/sector/%d/" % request.user.get_profile().sector.id)

def _view_sector_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile(), role__name="sector_manager_assistant")
	projects = responsibility.projects.all()
	for project in projects:
		project.reports = report_functions.get_submitted_and_overdue_reports(project)

		for report in project.reports:
			for schedule in report.schedules:
				schedule.comment_count = Comment.objects.filter(object_name='report', object_id=schedule.id).count()

	return render_response(request, "dashboard_sector_assistant.html", {'projects':projects})

def _view_project_manager_frontpage(request):
	responsibility = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name='project_manager')
	project = responsibility[0].projects.all()[0]
	return redirect("/project/%d/" % project.id)

def _view_project_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name="project_manager_assistant")
	project = responsibility[0].projects.all()[0]
	return redirect("/project/%d/" % project.id)

def _comments_sorting(x, y):
	return cmp(x.sent_on, y.sent_on)

@login_required
def view_dashboard_comments(request):
	user_account = request.user.get_profile()

	comments = set()
	for received_comment in CommentReceiver.objects.filter(is_read=False, receiver=user_account):
		comments.add(received_comment.comment)

	for received_comment in CommentReplyReceiver.objects.filter(is_read=False, receiver=user_account):
		comments.add(received_comment.reply.comment)

	comment_list = list(comments)
	comment_list.sort(_comments_sorting, reverse=True)

	for comment in comments:
		comment.is_read = CommentReceiver.objects.get(comment=comment, receiver=user_account).is_read

		receivers = CommentReplyReceiver.objects.filter(is_read=False, reply__comment=comment, receiver=user_account).order_by('reply__sent_on')
		replies = list()
		for receiver in receivers:
			replies.append(receiver.reply)
		comment.replies = replies

	object_list = list()
	object_dict = dict()

	for comment in comment_list:
		hash_str = "%s%d" % (comment.object_name, comment.object_id)
		if hash_str not in object_list:
			object = comments_functions.get_comment_object(comment.object_name, comment.object_id)

			if object:
				object_list.append(hash_str)
				object_dict[hash_str] = {'comment':comment, 'object':object, 'comments':[comment]}

		else:
			object_dict[hash_str]['comments'].append(comment)

	objects = list()
	for object_hash in object_list:
		objects.append(object_dict[object_hash])

	return render_response(request, "dashboard_comments.html", {'objects':objects})

@login_required
def view_dashboard_comments_outbox(request):
	user_account = request.user.get_profile()
	return redirect('view_dashboard_comments')

@login_required
def view_dashboard_my_projects(request):
	if utilities.user_has_role(request.user, 'sector_manager_assistant'):
		if request.method == 'POST':
			projects = request.POST.getlist('project')

			responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile())

			for project_id in projects:
				project = Project.objects.get(pk=project_id)
				responsibility.projects.add(project)

			return redirect('view_frontpage')

		else:
			responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile())
			master_plans = MasterPlan.objects.filter(sector=request.user.get_profile().sector).order_by('ref_no')
			
			for master_plan in master_plans:
				master_plan.projects = Project.objects.filter(master_plan=master_plan, parent_project=None)
				for project in master_plan.projects: project.responsible = _responsible_this_project(project, responsibility.projects.all())

			return render_response(request, "dashboard_sector_assistant_projects.html", {'master_plans':master_plans})
	else:
		return redirect('view_frontpage')

def _responsible_this_project(project, my_projects):
	for my_project in my_projects:
		if my_project.id == project.id:
			return True

	return False

#
# ADMIN
#
@login_required
def view_administer(request):
	return redirect('/administer/organization/')

@login_required
def view_administer_organization(request):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	sectors = Sector.objects.all().order_by('ref_no')
	for sector in sectors:
		sector.has_child = MasterPlan.objects.filter(sector=sector).count() > 0

	master_plans = MasterPlan.objects.all().order_by('ref_no')
	for master_plan in master_plans:
		master_plan.has_child = Plan.objects.filter(master_plan=master_plan).count() > 0 or Project.objects.filter(master_plan=master_plan).count()

		# Prepare year period
		year_period = master_plan.year_period
		master_plan.start = utilities.format_abbr_month_year(year_period.start)
		master_plan.end = utilities.format_abbr_month_year(year_period.end)

	return render_response(request, "administer_organization.html", {'sectors':sectors, 'master_plans':master_plans})

@login_required
def view_administer_organization_add_sector(request):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	if request.method == 'POST':
		form = SectorForm(request.POST)
		if form.is_valid():
			Sector.objects.create(ref_no=form.cleaned_data['ref_no'], name=form.cleaned_data['name'])

			return redirect('view_administer_organization')
	else:
		form = SectorForm()

	return render_response(request, "administer_organization_add_sector.html", {'form':form})

@login_required
def view_administer_organization_edit_sector(request, sector_id):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	sector = get_object_or_404(Sector, pk=sector_id)

	if request.method == 'POST':
		form = SectorForm(request.POST)
		if form.is_valid():
			sector.ref_no = form.cleaned_data['ref_no']
			sector.name = form.cleaned_data['name']
			sector.save()

			return redirect('view_administer_organization')

	else:
		form = SectorForm(initial={'ref_no':sector.ref_no, 'name':sector.name})

	return render_response(request, "administer_organization_edit_sector.html", {'form':form})

@login_required
def view_administer_organization_delete_sector(request, sector_id):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	sector = get_object_or_404(Sector, pk=sector_id)

	if not MasterPlan.objects.filter(sector=sector).count():
		sector.delete()
		set_message(request, u"ลบสำนัก%s เรียบร้อย" % sector.name)
	else:
		set_message(request, u"ไม่สามารถลบสำนัก%s ได้เนื่องจากยังมีข้อมูลแผนหลักอยู่ภายใต้" % sector.name)

	return redirect('view_administer_organization')

@login_required
def view_administer_organization_add_masterplan(request):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	if request.method == 'POST':
		form = MasterPlanForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			sector = form.cleaned_data['sector']
			year_start = form.cleaned_data['year_start'] - 543
			year_end = form.cleaned_data['year_end'] - 543

			# Get default month period, we know that there's existing one.
			default_month_period = MasterPlanMonthPeriod.objects.get(is_default=True)

			year_period_start = date(year_start, default_month_period.start_month, 1)
			year_period_end = date(year_end, default_month_period.end_month, 1)
			year_period, created = MasterPlanYearPeriod.objects.get_or_create(start=year_period_start, end=year_period_end, month_period=default_month_period)

			MasterPlan.objects.create(sector=sector, ref_no=ref_no, name=name, year_period=year_period)

			return redirect('view_administer_organization')

	else:
		form = MasterPlanForm()

	return render_response(request, "administer_organization_add_masterplan.html", {'form':form})

@login_required
def view_administer_organization_edit_masterplan(request, master_plan_id):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if request.method == 'POST':
		form = MasterPlanForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			sector = form.cleaned_data['sector']
			year_start = form.cleaned_data['year_start'] - 543
			year_end = form.cleaned_data['year_end'] - 543

			# Get default month period, we know that there's existing one.
			default_month_period = MasterPlanMonthPeriod.objects.get(is_default=True)

			year_period_start = date(year_start, default_month_period.start_month, 1)
			year_period_end = date(year_end, default_month_period.end_month, 1)
			year_period, created = MasterPlanYearPeriod.objects.get_or_create(start=year_period_start, end=year_period_end, month_period=default_month_period)

			master_plan.sector = sector
			master_plan.ref_no = ref_no
			master_plan.name = name
			master_plan.year_period = year_period
			master_plan.save()

			return redirect('view_administer_organization')

	else:
		year_start = master_plan.year_period.start.year + 543
		year_end = master_plan.year_period.end.year + 543
		form = MasterPlanForm(initial={'sector':master_plan.sector.id, 'ref_no':master_plan.ref_no, 'name':master_plan.name, 'year_start':year_start, 'year_end':year_end})

	return render_response(request, "administer_organization_edit_masterplan.html", {'form':form})

@login_required
def view_administer_organization_delete_masterplan(request, master_plan_id):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not Plan.objects.filter(master_plan=master_plan).count():
		master_plan.delete()
		set_message(request, u"ลบแผนหลัก%s เรียบร้อย" % master_plan.name)
	else:
		set_message(request, u"ไม่สามารถลบแผนหลัก%s ได้เนื่องจากยังมีข้อมูลกลุ่มแผนงานหรือแผนงานอยู่ภายใต้" % master_plan.name)

	return redirect('view_administer_organization')

@login_required
def view_administer_users(request):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	users = User.objects.filter(is_superuser=False).order_by('id')
	for user in users:
		responsibility = UserRoleResponsibility.objects.filter(user=user.get_profile())[0]
		user.role = GroupName.objects.get(group=responsibility.role).name
		
		if responsibility.role.name == 'project_manager' or responsibility.role.name == 'project_manager_assistant':
			user.projects = responsibility.projects.all()
	
	return render_response(request, "administer_users.html", {'users': users})

@login_required
def view_administer_users_add(request):
	if not request.user.is_superuser: return access_denied(request)

	if request.method == 'POST':
		form = UserAccountForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			role = form.cleaned_data['role']
			sector = Sector(id=form.cleaned_data['sector'])
			responsible = form.cleaned_data['responsible']

			password = utilities.make_random_user_password()

			user = User.objects.create_user(username, email, password=password)
			user_account = UserAccount.objects.get(user=user)
			user_account.first_name = first_name
			user_account.last_name = last_name
			user_account.random_password = password
			user_account.sector = sector
			user_account.save()

			group = Group.objects.get(name=role)

			user.groups.add(group)
			responsibility = UserRoleResponsibility.objects.create(user=user_account, role=group)

			if role == 'project_manager' or role == 'project_manager_assistant':
				project = Project.objects.get(pk=responsible)
				responsibility.projects.add(project)
			else:
				responsibility.sectors.add(sector)

			return redirect('view_administer_users_password', user.id)

	else:
		form = UserAccountForm()

	if request.POST.get('responsible'):
		responsible = request.POST['responsible']
		project = Project.objects.get(pk=responsible)

		master_plans = MasterPlan.objects.all()
		projects = Project.objects.filter(master_plan=project.master_plan, parent_project=None)

		return render_response(request, "administer_users_modify.html", {'mode':'create', 'form': form, 'master_plans':master_plans, 'projects':projects, 'responsible':project})
	else:
		return render_response(request, "administer_users_modify.html", {'mode':'create', 'form': form, 'responsible':''})

@login_required
def view_administer_users_edit(request, user_id):
	if not request.user.is_superuser: return access_denied(request)
	user = User.objects.get(pk=user_id)

	if request.method == 'POST':
		form = UserAccountForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			role = form.cleaned_data['role']
			sector = Sector(id=form.cleaned_data['sector'])
			responsible = form.cleaned_data['responsible']

			user.username = username
			user.email = email
			user.save()

			user_account = UserAccount.objects.get(user=user)
			user_account.first_name = first_name
			user_account.last_name = last_name
			user_account.sector = sector
			user_account.save()
			
			group = Group.objects.get(name=role)
			user.groups.clear()
			user.groups.add(group)
			
			UserRoleResponsibility.objects.filter(user=user_account).delete()
			responsibility = UserRoleResponsibility.objects.create(user=user_account, role=group)
			
			if role == 'project_manager' or role == 'project_manager_assistant':
				project = Project.objects.get(pk=responsible)
				responsibility.projects.clear()
				responsibility.projects.add(project)
			else:
				responsibility.sectors.clear()
				responsibility.sectors.add(sector)

			return redirect('view_administer_users')

		else:
			if request.POST.get('responsible'):
				responsible = request.POST['responsible']
				project = Project.objects.get(pk=responsible)

				master_plans = MasterPlan.objects.all()
				projects = Project.objects.filter(master_plan=project.master_plan, parent_project=None)
			else:
				project = None
				master_plans = None
				projects = None

	else:
		role = user.groups.all()[0].name
		if role == 'project_manager' or role == 'project_manager_assistant':
			responsible = UserRoleResponsibility.objects.filter(user=user.get_profile())[0].projects.all()[0].id
		else:
			responsible = None

		form = UserAccountForm(initial={\
			'username':user.username,\
			'email':user.email,\
			'first_name':user.get_profile().first_name,\
			'last_name':user.get_profile().last_name,\
			'role':role,\
			'sector':user.get_profile().sector,\
			'responsible':responsible});

		if responsible:
			project = Project.objects.get(pk=responsible)
			master_plans = MasterPlan.objects.all()
			projects = Project.objects.filter(master_plan=project.master_plan, parent_project=None)
		else:
			project = None
			master_plans = None
			projects = None

	return render_response(request, "administer_users_modify.html", {'mode':'edit', 'form': form, 'master_plans':master_plans, 'projects':projects, 'responsible':project})

@login_required
def view_administer_users_password(request, user_id):
	if not request.user.is_superuser: return access_denied(request)

	user = User.objects.get(pk=user_id)
	user_account = UserAccount.objects.get(user=user)

	return render_response(request, "administer_users_password.html", {'user_account': user_account})

@login_required
def view_administer_users_status(request, user_id):
	user_account = request.user.get_profile()
	if not request.user.is_superuser: return access_denied(request)

	user = User.objects.get(pk=user_id)
	user.is_active = not user.is_active
	user.save()

	return HttpResponse(simplejson.dumps({'status': 'complete'}))

#
# SECTOR
#
@login_required
def view_sectors(request):
	sectors = Sector.objects.all().order_by('ref_no')
	current_date = date.today().replace(day=1)

	for sector in sectors:
		sector.master_plans = MasterPlan.objects.filter(sector=sector, year_period__start__lte=current_date, year_period__end__gte=current_date).order_by('ref_no')

	return render_response(request, "sectors_overview.html", {'sectors':sectors})

@login_required
def view_sector_overview(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)
	current_date = date.today()
	current_year = current_date.year

	master_plans = MasterPlan.objects.filter(sector=sector, year_period__start__lte=current_date, year_period__end__gte=current_date).order_by('ref_no')

	return render_response(request, "sector_overview.html", {'sector':sector, 'master_plans':master_plans,})

@login_required
def view_sector_reports(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', sector): return access_denied(request)

	reports = Report.objects.filter(sector=sector).order_by('created')

	for report in reports:
		report.project_count = ReportProject.objects.filter(report=report).count()

	return render_response(request, "sector_reports.html", {'sector':sector, 'reports':reports})

@login_required
def view_sector_add_report(request, sector_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', sector): return access_denied(request)

	if request.method == 'POST':
		form = SectorReportForm(request.POST)
		if form.is_valid():
			report_name = form.cleaned_data['name']
			need_approval = form.cleaned_data['need_approval']
			schedule_cycle_length = form.cleaned_data['schedule_cycle_length']
			schedule_monthly_date = form.cleaned_data['schedule_monthly_date']
			notify_days = form.cleaned_data['notify_days']

			Report.objects.create(name=report_name, need_approval=need_approval, need_checkup=True, schedule_cycle_length=schedule_cycle_length, schedule_monthly_date=schedule_monthly_date, sector=sector, created_by=request.user.get_profile(), notify_days=notify_days)

			set_message(request, u"สร้างรายงาน%s เรียบร้อย" % report_name)

			return redirect('view_sector_reports', (sector.id))

	else:
		form = SectorReportForm()

	return render_response(request, "sector_report_add.html", {'sector':sector, 'form':form})

@login_required
def view_sector_edit_report(request, sector_id, report_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', sector): return access_denied(request)

	report = get_object_or_404(Report, pk=report_id)
	if request.method == 'POST':
		form = SectorReportForm(request.POST)
		if form.is_valid():
			report.name = form.cleaned_data['name']
			report.need_approval = form.cleaned_data['need_approval']
			report.notify_days = form.cleaned_data['notify_days']
			report.save()
			set_message(request, u"แก้ไขรายงาน%s เรียบร้อย" % report.name)

			return redirect('view_sector_reports', (sector.id))

	else:
		form = SectorReportForm(initial={'name':report.name, 'need_approval':report.need_approval, 'notify_days': report.notify_days})

	return render_response(request, "sector_report_edit.html", {'sector':sector, 'form':form})

@login_required
def view_sector_delete_report(request, sector_id, report_id):
	sector = get_object_or_404(Sector, pk=sector_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', sector): return access_denied(request)

	report = get_object_or_404(Report, pk=report_id)

	project_count = ReportProject.objects.filter(report=report).count()
	if not project_count:
		report.delete()
		set_message(request, u"ลบรายงาน%s เรียบร้อย" % report.name)
	else:
		set_message(request, u"ไม่สามารถลบรายงานได้เนื่องจากมีแผนงานที่ส่งรายงานนี้อยู่" % report_name)

	return redirect('view_sector_reports', (sector.id))

#
# MASTER PLAN
#
@login_required
def view_master_plan_overview(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	current_date = date.today()
	current_year = utilities.current_year_number()

	# Plans
	plans = Plan.objects.filter(master_plan=master_plan)
	for plan in plans:
		plan.current_projects = Project.objects.filter(plan=plan, start_date__lte=current_date, end_date__gte=current_date)

	master_plan.plans = plans

	return render_response(request, "master_plan_overview.html", {'master_plan':master_plan, 'current_year':current_year})

@login_required
def view_master_plan_plans(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	plans = Plan.objects.filter(master_plan=master_plan)

	for plan in plans:
		plan.projects = Project.objects.filter(plan=plan).order_by('-start_date')

	return render_response(request, "master_plan_plans.html", {'master_plan':master_plan, 'plans':plans})

@login_required
def view_master_plan_organization(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	plans = Plan.objects.filter(master_plan=master_plan)

	for plan in plans:
		plan.projects = Project.objects.filter(plan=plan).order_by('-start_date')
		for project in plan.projects:
			if Project.objects.filter(parent_project=project).count() or ReportSchedule.objects.filter(report_project__project=project).exclude(state=NO_ACTIVITY).count():
				project.has_child = True

	return render_response(request, "master_plan_organization.html", {'master_plan':master_plan, 'plans':plans})

@login_required
def view_master_plan_add_plan(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	if request.method == 'POST':
		form = PlanForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			plan = Plan.objects.create(ref_no=cleaned_data['ref_no'], name=cleaned_data['name'], master_plan=master_plan)
			set_message(request, u"สร้างกลุ่มแผนงาน%s เรียบร้อย" % plan.name)

			return redirect('view_master_plan_organization', (master_plan_id))
	else:
		form = PlanForm()

	return render_response(request, "master_plan_add_plan.html", {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_edit_plan(request, master_plan_id, plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	plan = get_object_or_404(Plan, pk=plan_id)

	if request.method == 'POST':
		form = PlanForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			plan.ref_no = cleaned_data['ref_no']
			plan.name = cleaned_data['name']
			plan.save()
			set_message(request, u"แก้ไขกลุ่มแผนงาน%s เรียบร้อย" % plan.name)

			return redirect('view_master_plan_organization', (master_plan_id))
	else:
		form = PlanForm(initial={'ref_no':plan.ref_no, 'name':plan.name})

	return render_response(request, "master_plan_edit_plan.html", {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_delete_plan(request, master_plan_id, plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)
	plan = get_object_or_404(Plan, pk=plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	if not Project.objects.filter(plan=plan).count():
		plan.delete()
		set_message(request, u"ลบกลุ่มแผนงาน%s เรียบร้อย" % plan.name)
	else:
		set_message(request, u"ไม่สามารถลบกลุ่มแผนงาน%s ได้ เนื่องจากมีแผนงานที่อยู่ภายใต้" % plan.name)

	return redirect('view_master_plan_organization', (master_plan_id))

@login_required
def view_master_plan_add_project(request, master_plan_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	class CustomMasterPlanAddProjectForm(MasterPlanAddProjectForm):
		plan = PlanChoiceField(queryset=Plan.objects.filter(master_plan=master_plan), label="สังกัดกลุ่มแผนงาน", empty_label=None)
		reports = ReportMultipleChoiceField(queryset=Report.objects.filter(sector=master_plan.sector), label="รายงานที่ต้องส่ง")

	if request.method == 'POST':
		form = CustomMasterPlanAddProjectForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			project = Project()
			project.sector = master_plan.sector
			project.master_plan = master_plan
			project.plan = cleaned_data['plan']
			project.prefix_name = Project.PROJECT_IS_PROGRAM

			project.ref_no = cleaned_data['ref_no']
			project.name = cleaned_data['name']
			project.start_date = cleaned_data['start_date']
			project.end_date = cleaned_data['end_date']
			project.save()

			for report in cleaned_data['reports']:
				report_project = ReportProject.objects.create(report=report, project=project)

				# Create ReportSchedule
				if report.schedule_cycle == 3:
					# Find next schedule date,
					# if today(project created day) pass this month schedule
					# date then use schedule date of next month
					today = date.today()

					this_month_schedule_date = utilities.schedule_month_date(report, today.year, today.month)
					if today > this_month_schedule_date:
						year, month = next_month(today.year, today.month)
						this_month_schedule_date = utilities.schedule_month_date(report, year, month)

					cycle_length = report.schedule_cycle_length
					cycle_counter = 0
					while this_month_schedule_date <= project.end_date:
						if cycle_counter % cycle_length == 0:
							report_schedule = ReportSchedule.objects.create(
								report_project=report_project,
								due_date=this_month_schedule_date
							)

						year, month = next_month(this_month_schedule_date.year, this_month_schedule_date.month)
						this_month_schedule_date = utilities.schedule_month_date(report, year, month)
						cycle_counter += 1

			set_message(request, u"สร้างแผนงาน %s เรียบร้อยแล้ว" % project.name)
			return redirect('view_master_plan_organization', (master_plan_id))
	else:
		form = CustomMasterPlanAddProjectForm()

	return render_response(request, "master_plan_add_project.html", {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_edit_project(request, master_plan_id, project_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	project = get_object_or_404(Project, pk=project_id)

	class CustomMasterPlanAddProjectForm(MasterPlanEditProjectForm):
		plan = PlanChoiceField(queryset=Plan.objects.filter(master_plan=master_plan), label="สังกัดกลุ่มแผนงาน", empty_label=None)
		reports = ReportMultipleChoiceField(queryset=Report.objects.filter(sector=master_plan.sector), label="รายงานที่ต้องส่ง")

	if request.method == 'POST':
		form = CustomMasterPlanAddProjectForm(request.POST)
		if form.is_valid():
			cleaned_data = form.cleaned_data
			project.plan = cleaned_data['plan']
			project.ref_no = cleaned_data['ref_no']
			project.name = cleaned_data['name']
			project.save()

			report_old = [report_project.report for report_project in ReportProject.objects.filter(project=project, is_active=True)]
			report_new = cleaned_data['reports']

			# Find cancelled Report
			cancelled_reports = set(report_old) - set(report_new)
			for cancelled_report in cancelled_reports:
				# Delete advanced report schedule that has no activities
				report_project = ReportProject.objects.get(report=cancelled_report, project=project)
				ReportSchedule.objects.filter(report_project=report_project, due_date__gte=date.today(), state=NO_ACTIVITY).delete()
				report_project.is_active = False
				report_project.save()

			# Add new Report
			new_reports = set(report_new) - set(report_old)
			for report in new_reports:
				report_project, created = ReportProject.objects.get_or_create(report=report, project=project)
				report_project.is_active = True
				report_project.save()

				# Create ReportSchedule
				if report.schedule_cycle == 3:
					# Find next schedule date,
					# if today(project created day) pass this month schedule
					# date then use schedule date of next month
					today = date.today()

					this_month_schedule_date = utilities.schedule_month_date(report, today.year, today.month)
					if today > this_month_schedule_date:
						year, month = next_month(today.year, today.month)
						this_month_schedule_date = utilities.schedule_month_date(report, year, month)

					cycle_length = report.schedule_cycle_length
					cycle_counter = 0
					while this_month_schedule_date <= project.end_date:
						if cycle_counter % cycle_length == 0:
							report_schedule = ReportSchedule.objects.create(
								report_project=report_project,
								due_date=this_month_schedule_date
							)

						year, month = next_month(this_month_schedule_date.year, this_month_schedule_date.month)
						this_month_schedule_date = utilities.schedule_month_date(report, year, month)
						cycle_counter += 1

			set_message(request, u"แก้ไขแผนงาน%s เรียบร้อย" % project.name)
			return redirect('view_master_plan_organization', (master_plan_id))
	else:
		report_projects = ReportProject.objects.filter(project=project, is_active=True)
		form = CustomMasterPlanAddProjectForm(initial={'plan':project.plan.pk, 'ref_no':project.ref_no, 'name':project.name, 'description':project.description, 'reports':[report_project.report.id for report_project in report_projects]})

	return render_response(request, "master_plan_edit_project.html", {'master_plan':master_plan, 'form':form})

@login_required
def view_master_plan_delete_project(request, master_plan_id, project_id):
	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not utilities.responsible(request.user, 'sector_manager_assistant,sector_admin', master_plan.sector): return access_denied(request)

	project = get_object_or_404(Project, pk=project_id)

	if Project.objects.filter(parent_project=project).count() or ReportSchedule.objects.filter(report_project__project=project).exclude(state=NO_ACTIVITY).count():
		set_message(request, u"ไม่สามารถลบแผนงาน%s ได้ เนื่องจากแผนงานยังมีโครงการหรือรายงานอยู่" % project.name)

	else:
		ReportSchedule.objects.filter(report_project__project=project, state=NO_ACTIVITY).delete()
		ReportProject.objects.filter(project=project).delete()
		project.delete()
		set_message(request, u"ลบแผนงาน%s เรียบร้อย" % project.name)

	return redirect('view_master_plan_organization', (master_plan_id))

#
# PROJECT
#
@login_required
def view_project_overview(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	current_date = date.today()

	if not project.parent_project:
		current_projects = Project.objects.filter(parent_project=project, start_date__lte=current_date, end_date__gte=current_date)

		report_schedules = ReportSchedule.objects.filter(report_project__project=project).filter(Q(state=APPROVE_ACTIVITY) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_approval=False)) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_checkup=False))).order_by('-due_date')[:5]

		return render_response(request, "project_overview.html", {'project':project, 'current_projects':current_projects, 'report_schedules':report_schedules})

	else:
		current_activities = Activity.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)

		return render_response(request, "project_overview.html", {'project':project, 'current_activities':current_activities})

@login_required
def view_project_projects(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	projects = Project.objects.filter(parent_project=project).order_by('-start_date')

	return render_response(request, "project_projects.html", {'project':project, 'projects':projects})

@login_required
def view_project_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		if request.method == "POST":
			form = ProjectForm(request.POST)
			if form.is_valid():
				created_project = Project.objects.create(
					sector=project.sector,
					master_plan=project.master_plan,
					parent_project=project,
					prefix_name=Project.PROJECT_IS_PROJECT,
					ref_no=form.cleaned_data['ref_no'],
					name=form.cleaned_data['name'],
					start_date=form.cleaned_data['start_date'],
					end_date=form.cleaned_data['end_date']
				)

				set_message(request, u"สร้างโครงการ%s เรียบร้อย" % project.name)

				return redirect('view_project_overview', (created_project.id))

		else:
			form = ProjectForm()

		return render_response(request, "project_projects_add.html", {'project':project, 'form':form})

	else:
		return redirect('view_project_projects', (project.id))

@login_required
def view_project_edit(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if request.method == "POST":
			form = ProjectForm(request.POST)
			if form.is_valid():
				project.ref_no = form.cleaned_data.get('ref_no')
				project.name = form.cleaned_data.get('name')
				project.start_date = form.cleaned_data.get('start_date')
				project.end_date = form.cleaned_data.get('end_date')
				project.save()

				set_message(request, u"แก้ไขโครงการ%s เรียบร้อย" % project.name)

				return redirect('view_project_overview', (project.id))

		else:
			form = ProjectForm(project.__dict__)

		return render_response(request, "project_projects_edit.html", {'project':project, 'form':form})

	else:
		return redirect('view_project_projects', (project.id))

@login_required
def view_project_delete(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if Activity.objects.filter(project=project).count():
			set_message(request, 'ยังมีกิจกรรมอยู่ภายใต้โครงการ ต้องลบกิจกรรมก่อนลบโครงการ')
			return redirect('view_project_overview', (project.id))
		else:
			project.delete()
			set_message(request, u"ลบโครงการ%s เรียบร้อย" % project.name)
			return redirect('view_project_projects', (head_project.id))

	else:
		return redirect('view_project_projects', (head_project.id))

	return render_response(request, "project_projects_edit.html", {'project':project, 'form':form})

@login_required
def view_project_reports(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	report_projects = ReportProject.objects.filter(project=project)

	for report_project in report_projects:
		report_project.schedules = ReportSchedule.objects.filter(report_project=report_project).filter(Q(state=APPROVE_ACTIVITY) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_approval=False)) | (Q(state=SUBMIT_ACTIVITY) & Q(report_project__report__need_checkup=False))).order_by('-due_date')

		year_list = set()
		for schedule in report_project.schedules: year_list.add(schedule.due_date.year)
		year_list = sorted(year_list, reverse=True)

		report_project.year_list = year_list

	return render_response(request, "project_reports.html", {'project':project, 'report_projects':report_projects})

@login_required
def view_project_reports_list(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	report_projects = ReportProject.objects.filter(project=project)

	sector_reports = list()
	project_reports = list()

	for report_project in report_projects:
		if report_project.report.sector:
			sector_reports.append(report_project.report)
		else:
			project_reports.append(report_project.report)

	return render_response(request, "project_reports_list.html", {'project':project, 'sector_reports':sector_reports, 'project_reports':project_reports})

@login_required
def view_project_reports_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	if request.method == 'POST':
		form = AddProjectReportForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			need_checkup = form.cleaned_data['need_checkup']
			need_approval = form.cleaned_data['need_approval']
			schedule_cycle_length = int(form.cleaned_data['schedule_cycle_length'])
			schedule_monthly_date = int(form.cleaned_data['schedule_monthly_date'])
			start_date = form.cleaned_data['start_date']
			end_date = form.cleaned_data['end_date']

			report = Report.objects.create(
				name=name,
				need_checkup=need_checkup,
				need_approval=need_approval,
				created_by=UserAccount.objects.get(user=request.user),
				schedule_cycle_length=schedule_cycle_length,
				schedule_monthly_date=schedule_monthly_date)

			report_project = ReportProject.objects.create(report=report, project=project)

			# Create ReportSchedule
			if report.schedule_cycle == 3:
				# Find next schedule date,
				# if today(project created day) pass this month schedule
				# date then use schedule date of next month
				today = date.today()

				this_month_schedule_date = utilities.schedule_month_date(report, today.year, today.month)
				if today > this_month_schedule_date:
					year, month = next_month(today.year, today.month)
					this_month_schedule_date = utilities.schedule_month_date(report, year, month)

				cycle_length = report.schedule_cycle_length
				cycle_counter = 0
				while this_month_schedule_date <= end_date:
					if cycle_counter % cycle_length == 0:
						report_schedule, created = ReportSchedule.objects.get_or_create(
							report_project=report_project,
							due_date=this_month_schedule_date
						)

					year, month = next_month(this_month_schedule_date.year, this_month_schedule_date.month)
					this_month_schedule_date = utilities.schedule_month_date(report, year, month)
					cycle_counter += 1

			set_message(request, u"สร้างประเภทรายงาน %s แล้ว" % name)
			return redirect('view_project_reports_list', (project_id))

	else:
		form = AddProjectReportForm()

	return render_response(request, "project_reports_add.html", {'project':project, 'form':form})

@login_required
def view_project_report_edit(request, project_id, report_id):
	project = get_object_or_404(Project, pk=project_id)
	report = get_object_or_404(Report, pk=report_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	if request.method == 'POST':
		form = EditProjectReportForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			need_checkup = form.cleaned_data['need_checkup']
			need_approval = form.cleaned_data['need_approval']

			report.name = name
			report.need_checkup = need_checkup
			report.need_approval = need_approval
			report.save()

			set_message(request, u"บันทึกการแก้ไขรายงาน %s เรียบร้อยแล้ว" % name)
			return redirect('view_project_reports_list', (project_id))
	else:
		form = EditProjectReportForm(initial=dict(
			name=report.name,
			need_checkup=report.need_checkup,
			need_approval=report.need_approval))

	return render_response(request, "project_reports_edit.html", {'project':project, 'form':form})

@login_required
def view_project_reports_send(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	reports = report_functions.get_nextdue_and_overdue_reports(project_id)

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
		return redirect('view_project_reports', (project.id))

	for report in reports:
		for schedule in report.schedules:
			schedule.comment_count = Comment.objects.filter(object_name='report', object_id=schedule.id).count()

	return render_response(request, "project_reports_send.html", {'project':project, 'reports':reports})

# Helper function to find previous and next month.
def prev_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	month_index = MONTH.index(month)
	prev_index = month_index - num
	if abs(prev_index) > 12:
		prev_index = 12 % prev_index

	if prev_index < 0:
		year = year + (prev_index / 12)

	return (year, MONTH[prev_index])

def next_month(year, month, num=1):
	'''Return (year, month)'''
	MONTH = range(1, 13)
	delta = num
	index = month + num

	return (year + (index / 13), MONTH[index % 12 - 1])

@login_required
def view_project_activities(request, project_id):
	project = get_object_or_404(Project, pk=project_id)
	current_date = date.today()

	activities = Activity.objects.filter(project=project).order_by('-start_date')

	# Find activities in past month, current month and next month.
	num = 3
	prev_month_ = prev_month(current_date.year, current_date.month, num)
	start = date(*prev_month_, day=1)
	next_month_ = next_month(current_date.year, current_date.month, num)
	end = date(*next_month_, day=calendar.monthrange(*next_month_)[1])

	prev_month_ = "%04d%02d" % prev_month(current_date.year, current_date.month)
	next_month_ = "%04d%02d" % next_month(current_date.year, current_date.month)

	recent_activities = Activity.objects.filter(project=project).filter( \
		Q(start_date__lte=start) & Q(end_date__gte=end) | \
		Q(start_date__lte=end) & Q(start_date__gte=start) | \
		Q(end_date__lte=end) & Q(end_date__gte=start))

	return render_response(request, "project_activities.html", {'project':project, 'activities':activities, 'recent_activities':recent_activities,'prev_month':prev_month_,'next_month':next_month_})

@login_required
def view_project_activities_ajax(request, project_id, yearmonth):
	project = get_object_or_404(Project, pk=project_id)

	year = int(yearmonth[:4])
	month = int(yearmonth[4:])

	# Find activities in past month, current month and future month.
	num = 3
	prev_month_ = prev_month(year, month, num)
	next_month_ = next_month(year, month, num)

	start = date(*prev_month_, day=1)
	end = date(*next_month_, day=calendar.monthrange(*next_month_)[1])

	prev_month_ = "%04d%02d" % prev_month(year, month)
	next_month_ = "%04d%02d" % next_month(year, month)

	recent_activities = Activity.objects.filter(project=project).filter( \
		Q(start_date__lte=start) & Q(end_date__gte=end) | \
		Q(start_date__lte=end) & Q(start_date__gte=start) | \
		Q(end_date__lte=end) & Q(end_date__gte=start))

	return render_response(request, "project_activities_ajax.html", {'recent_activities':recent_activities,'prev_month':prev_month_,'next_month':next_month_})

@login_required
def view_activity_add(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if request.method == "POST":
			form = ActivityForm(request.POST)
			if form.is_valid():
				activity = Activity.objects.create(project=project,\
					name=form.cleaned_data['name'],\
					start_date=form.cleaned_data['start_date'],\
					end_date=form.cleaned_data['end_date'],\
					description=form.cleaned_data['description'],\
					location=form.cleaned_data['location'],\
					result_goal=form.cleaned_data['result_goal'],\
					result_real=form.cleaned_data['result_real'],\
					)

				set_message(request, u"สร้างกิจกรรม%s เรียบร้อย" % activity.name)

				return redirect('view_activity_overview', (activity.id))

		else:
			form = ActivityForm()

		return render_response(request, "project_activity_add.html", {'project':project, 'form':form})

	else:
		return redirect('view_project_activities', (project.id))

@login_required
def view_activity_edit(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)
	project = activity.project

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		if request.method == 'POST':
			form = ActivityForm(request.POST)
			if form.is_valid():
				activity.name        = form.cleaned_data['name']
				activity.start_date  = form.cleaned_data['start_date']
				activity.end_date    = form.cleaned_data['end_date']
				activity.description = form.cleaned_data['description']
				activity.location    = form.cleaned_data['location']
				activity.result_goal = form.cleaned_data['result_goal']
				activity.result_real = form.cleaned_data['result_real']
				activity.save()

				set_message(request, u"แก้ไขกิจกรรม%s เรียบร้อย" % activity.name)

				return redirect('view_activity_overview', (activity.id))

		else:
			form = ActivityForm(activity.__dict__)

		return render_response(request, "project_activity_edit.html", {'activity':activity, 'form':form})

	else:
		return redirect('view_activity_overview', (activity.id))

@login_required
def view_activity_delete(request, activity_id):
	activity = Activity.objects.get(pk=activity_id)
	project = activity.project

	head_project = project.parent_project if project.parent_project else project

	if utilities.responsible(request.user, 'project_manager,project_manager_assistant', head_project):
		activity.delete()
		set_message(request, 'ลบกิจกรรมเรียบร้อย')

	return redirect("/project/%d/activities/" % project.id)

@login_required
def view_project_comments(request, project_id):
	project = get_object_or_404(Project, pk=project_id)

	comments = comments_functions.retrieve_visible_comments(request, 'project', project.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='project',\
		comment__object_id=project.id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='project',\
		reply__comment__object_id=project.id).update(is_read=True)

	return render_response(request, "project_comments.html", {'project':project, 'comments':comments})

#
# ACTIVITY
#
@login_required
def view_activity_overview(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)
	return render_response(request, "activity_overview.html", {'activity':activity,})

@login_required
def view_activity_comments(request, activity_id):
	activity = get_object_or_404(Activity, pk=activity_id)

	comments = comments_functions.retrieve_visible_comments(request, 'activity', activity.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(), comment__object_name='activity', \
		comment__object_id=activity_id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='activity',\
		reply__comment__object_id=activity_id).update(is_read=True)

	return render_response(request, "activity_comments.html", {'activity':activity, 'comments':comments,})

#
# REPORT
#
@login_required
def view_report_overview(request, report_id):
	report_schedule = get_object_or_404(ReportSchedule, pk=report_id)

	if request.method == 'POST':
		project = report_schedule.report_project.project

		if utilities.responsible(request.user, 'project_manager,project_manager_assistant', project):
			return redirect('view_report_overview', (report_schedule.id))

		submit_type = request.POST.get('submit')

		if submit_type == 'submit-file':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)

			file_response = ReportScheduleFileResponse.objects.create(schedule=schedule, uploaded_by=request.user.get_profile())

			# Uploading directory
			uploading_directory = "%s/%d/" % (settings.REPORT_SUBMIT_FILE_PATH, schedule.id)
			if not os.path.exists(uploading_directory): os.makedirs(uploading_directory)

			# Uploading file
			uploading_file = request.FILES['uploading_file']
			(file_name, separator, file_ext) = uploading_file.name.rpartition('.')

			unique_filename = '%s.%s' % (file_name, file_ext)
			if os.path.isfile('%s%s' % (uploading_directory, unique_filename)):
				# Duplicated filename
				suffix_counter = 1

				while os.path.isfile('%s%s(%d).%s' % (uploading_directory, file_name, suffix_counter, file_ext)):
					suffix_counter = suffix_counter + 1

				unique_filename = '%s(%d).%s' % (file_name, suffix_counter, file_ext)

			file_response.filename = unique_filename
			file_response.save()

			destination = open(uploading_directory + unique_filename, 'wb')
			for chunk in request.FILES['uploading_file'].chunks(): destination.write(chunk)
			destination.close()

		elif submit_type == 'submit-text':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)

			text = request.POST.get("text")

			try:
				text_response = ReportScheduleTextResponse.objects.get(schedule=schedule)

			except ReportScheduleTextResponse.DoesNotExist:
				text_response = ReportScheduleTextResponse.objects.create(schedule=schedule, submitted_by=request.user.get_profile())

			text_response.text = text
			text_response.save()

		elif submit_type == 'submit-report':
			schedule_id = request.POST.get("schedule_id")
			schedule = ReportSchedule.objects.get(pk=schedule_id)
			
			from datetime import datetime

			schedule.state = SUBMIT_ACTIVITY
			schedule.submitted_on = datetime.now()
			schedule.approval_on = None
			schedule.save()

		return redirect('/report/%d/' % schedule.id)

	current_date = date.today()

	if report_schedule.state == NO_ACTIVITY and report_schedule.due_date < current_date:
		report_schedule.status_code = 'overdue'
	elif report_schedule.state == NO_ACTIVITY:
		report_schedule.status_code = 'not_submitted'
	elif report_schedule.state == SUBMIT_ACTIVITY and not report_schedule.report_project.report.need_approval:
		report_schedule.status_code = 'submitted'
	elif report_schedule.state == SUBMIT_ACTIVITY and report_schedule.report_project.report.need_approval:
		report_schedule.status_code = 'waiting'
	elif report_schedule.state == APPROVE_ACTIVITY:
		report_schedule.status_code = 'approved'
	elif report_schedule.state == APPROVE_ACTIVITY:
		report_schedule.status_code = 'rejected'

	report_schedule.allow_modifying = report_schedule.status_code in ('overdue', 'not_submitted', 'rejected')

	try:
		report_schedule.text_response = ReportScheduleTextResponse.objects.get(schedule=report_schedule)
	except ReportScheduleTextResponse.DoesNotExist:
		report_schedule.text_response = ''

	report_schedule.files = ReportScheduleFileResponse.objects.filter(schedule=report_schedule)

	return render_response(request, "report_overview.html", {'report_schedule':report_schedule, 'REPORT_SUBMIT_FILE_URL':settings.REPORT_SUBMIT_FILE_URL, })

@login_required
def view_report_comments(request, report_id):
	report = get_object_or_404(ReportSchedule, pk=report_id)

	comments = comments_functions.retrieve_visible_comments(request, 'report', report.id)

	# Mark comments as read
	CommentReceiver.objects.filter(receiver=request.user.get_profile(),\
		comment__object_name='report',\
		comment__object_id=report.id).update(is_read=True)

	CommentReplyReceiver.objects.filter(receiver=request.user.get_profile(),\
		reply__comment__object_name='report',\
		reply__comment__object_id=report.id).update(is_read=True)

	return render_response(request, "report_comments.html", {'report_schedule':report, 'comments':comments, })
