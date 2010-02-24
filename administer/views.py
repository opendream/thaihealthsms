# -*- encoding: utf-8 -*-

from datetime import date

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string

from administer.forms import *

from accounts.models import UserAccount, UserRoleResponsibility
from domain.models import *

from kpi.forms import ModifyKPIForm, ModifyKPICategoryForm
from kpi.models import *

from helper import utilities
from helper.message import set_message
from helper.shortcuts import render_response, access_denied

@login_required
def view_administer(request):
	return redirect('/administer/organization/')

#
# ORGANIZATION
#

@login_required
def view_administer_organization(request):
	if not request.user.is_superuser: return access_denied(request)

	sectors = Sector.objects.all().order_by('ref_no')
	for sector in sectors:
		sector.has_child = MasterPlan.objects.filter(sector=sector).count() > 0

	master_plans = MasterPlan.objects.all().order_by('ref_no')
	for master_plan in master_plans:
		master_plan.has_child = Plan.objects.filter(master_plan=master_plan).count() > 0 or Project.objects.filter(master_plan=master_plan).count()

	return render_response(request, "page_admin/administer_organization.html", {'sectors':sectors, 'master_plans':master_plans})

@login_required
def view_administer_organization_add_sector(request):
	if not request.user.is_superuser: return access_denied(request)

	if request.method == 'POST':
		form = ModifySectorForm(request.POST)
		if form.is_valid():
			Sector.objects.create(ref_no=form.cleaned_data['ref_no'], name=form.cleaned_data['name'])
			
			set_message(request, u'เพิ่มสำนักเรียบร้อย')
			return redirect('view_administer_organization')
	else:
		form = ModifySectorForm()

	return render_response(request, "page_admin/administer_organization_sector_modify.html", {'form':form})

@login_required
def view_administer_organization_edit_sector(request, sector_id):
	if not request.user.is_superuser: return access_denied(request)

	sector = get_object_or_404(Sector, pk=sector_id)

	if request.method == 'POST':
		form = ModifySectorForm(request.POST)
		if form.is_valid():
			sector.ref_no = form.cleaned_data['ref_no']
			sector.name = form.cleaned_data['name']
			sector.save()

			set_message(request, u'แก้ไขสำนักเรียบร้อย')
			return redirect('view_administer_organization')

	else:
		form = ModifySectorForm(initial={'sector_id':sector.id, 'ref_no':sector.ref_no, 'name':sector.name})

	return render_response(request, "page_admin/administer_organization_sector_modify.html", {'sector':sector, 'form':form})

@login_required
def view_administer_organization_delete_sector(request, sector_id):
	if not request.user.is_superuser: return access_denied(request)

	sector = get_object_or_404(Sector, pk=sector_id)

	if not MasterPlan.objects.filter(sector=sector).count():
		sector.delete()
		set_message(request, u"ลบสำนักเรียบร้อย")
	else:
		set_message(request, u"ไม่สามารถลบสำนัก%s ได้เนื่องจากยังมีข้อมูลแผนหลักอยู่ภายใต้" % sector.name)

	return redirect('view_administer_organization')

@login_required
def view_administer_organization_add_masterplan(request):
	if not request.user.is_superuser: return access_denied(request)

	if request.method == 'POST':
		form = ModifyMasterPlanForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			sector = form.cleaned_data['sector']
			month_span = MonthSpan.objects.get(is_default=True)
			
			MasterPlan.objects.create(sector=sector, ref_no=ref_no, name=name, month_span=month_span)
			
			set_message(request, u'เพิ่มแผนหลักเรียบร้อย')
			return redirect('view_administer_organization')

	else:
		form = ModifyMasterPlanForm()
	
	has_sectors = Sector.objects.all().count() > 0
	return render_response(request, "page_admin/administer_organization_masterplan_modify.html", {'form':form, 'has_sectors':has_sectors})

@login_required
def view_administer_organization_edit_masterplan(request, master_plan_id):
	if not request.user.is_superuser: return access_denied(request)

	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if request.method == 'POST':
		form = ModifyMasterPlanForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			sector = form.cleaned_data['sector']
			
			master_plan.sector = sector
			master_plan.ref_no = ref_no
			master_plan.name = name
			master_plan.save()
			
			set_message(request, u'แก้ไขแผนหลักเรียบร้อย')
			return redirect('view_administer_organization')

	else:
		
		form = ModifyMasterPlanForm(initial={'master_plan_id':master_plan.id, 'sector':master_plan.sector.id, 'ref_no':master_plan.ref_no, 'name':master_plan.name})

	return render_response(request, 'page_admin/administer_organization_masterplan_modify.html', {'master_plan':master_plan, 'form':form, 'has_sectors':has_sectors})

@login_required
def view_administer_organization_delete_masterplan(request, master_plan_id):
	if not request.user.is_superuser: return access_denied(request)

	master_plan = get_object_or_404(MasterPlan, pk=master_plan_id)

	if not Plan.objects.filter(master_plan=master_plan).count():
		master_plan.delete()
		set_message(request, u'ลบแผนหลักเรียบร้อย')
	else:
		set_message(request, u'ไม่สามารถลบแผนหลัก%s ได้เนื่องจากยังมีข้อมูลกลุ่มแผนงานหรือแผนงานอยู่ภายใต้' % master_plan.name)

	return redirect('view_administer_organization')

#
# USERS
#

@login_required
def view_administer_users(request):
	if not request.user.is_superuser: return access_denied(request)

	users = User.objects.filter(is_superuser=False).order_by('id')
	for user in users:
		responsibility = UserRoleResponsibility.objects.filter(user=user.get_profile())[0]
		user.role = GroupName.objects.get(group=responsibility.role).name
		
		if responsibility.role.name == 'project_manager' or responsibility.role.name == 'project_manager_assistant':
			user.projects = responsibility.projects.all()
	
	return render_response(request, "page_admin/administer_users.html", {'users': users})

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
			sector = form.cleaned_data['sector']
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
			
			email_render_dict = {'username':username, 'password':password, 'settings':settings, 'site':Site.objects.get_current()}
			email_subject = render_to_string('email/create_user_subject.txt', email_render_dict)
			email_message = render_to_string('email/create_user_message.txt', email_render_dict)
			
			send_mail(email_subject, email_message, settings.SYSTEM_NOREPLY_EMAIL, [email])
			
			return redirect('view_administer_users_password', user.id)

	else:
		form = UserAccountForm()

	if request.POST.get('responsible'):
		responsible = request.POST['responsible']
		project = Project.objects.get(pk=responsible)

		master_plans = MasterPlan.objects.all()
		projects = Project.objects.filter(master_plan=project.master_plan, parent_project=None)

		return render_response(request, "page_admin/administer_users_modify.html", {'mode':'create', 'form': form, 'master_plans':master_plans, 'projects':projects, 'responsible':project})
	else:
		return render_response(request, "page_admin/administer_users_modify.html", {'mode':'create', 'form': form, 'responsible':''})

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
			sector = form.cleaned_data['sector']
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
			
			set_message(request, u"แก้ไขข้อมูลผู้ใช้เรียบร้อย")
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
			'sector':user.get_profile().sector.id,\
			'responsible':responsible});

		if responsible:
			project = Project.objects.get(pk=responsible)
			master_plans = MasterPlan.objects.all()
			projects = Project.objects.filter(master_plan=project.master_plan, parent_project=None)
		else:
			project = None
			master_plans = None
			projects = None

	return render_response(request, "page_admin/administer_users_modify.html", {'mode':'edit', 'form': form, 'master_plans':master_plans, 'projects':projects, 'responsible':project})

@login_required
def view_administer_users_password(request, user_id):
	if not request.user.is_superuser: return access_denied(request)

	user = User.objects.get(pk=user_id)
	new_user_account = UserAccount.objects.get(user=user)

	return render_response(request, "page_admin/administer_users_password.html", {'new_user_account': new_user_account})

#
# KPI
#

@login_required
def view_administer_kpi(request):
	if not request.user.is_superuser: return access_denied(request)
	
	category_list = KPI.objects.filter(master_plan=None).values('category').distinct()
	
	kpi_categories = list()
	for category_id in category_list:
		category = KPICategory.objects.get(pk=category_id['category'])
		category.kpis = KPI.objects.filter(master_plan=None, category=category).order_by('ref_no')
		
		for kpi in category.kpis:
			kpi.has_child = KPISchedule.objects.filter(kpi=kpi).count() > 0
		
		kpi_categories.append(category)
	
	return render_response(request, "page_admin/administer_kpi.html", {'kpi_categories':kpi_categories})

@login_required
def view_administer_kpi_add(request):
	if not request.user.is_superuser: return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyKPIForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			category = form.cleaned_data['category']
			unit_name = form.cleaned_data['unit_name']
			visible_to_project = form.cleaned_data['visible_to_project']
			
			kpi = KPI.objects.create(ref_no=ref_no,\
				name=name,\
				category=category,\
				unit_name=unit_name,\
				is_visible_to_project=visible_to_project,\
				created_by=request.user.get_profile())
			
			set_message(request, u"สร้างตัวชี้วัดเรียบร้อย")
			return redirect('view_administer_kpi')
		
	else:
		form = ModifyKPIForm()
	
	has_categories = KPICategory.objects.all().count() > 0
	return render_response(request, "page_admin/administer_kpi_modify.html", {'form':form, 'has_categories':has_categories})

@login_required
def view_administer_kpi_edit(request, kpi_id):
	if not request.user.is_superuser: return access_denied(request)
	
	kpi = KPI.objects.get(pk=kpi_id)
	
	if request.method == 'POST':
		form = ModifyKPIForm(request.POST)
		if form.is_valid():
			ref_no = form.cleaned_data['ref_no']
			name = form.cleaned_data['name']
			category = form.cleaned_data['category']
			unit_name = form.cleaned_data['unit_name']
			visible_to_project = form.cleaned_data['visible_to_project']
			
			kpi.ref_no = ref_no
			kpi.name = name
			kpi.category = category
			kpi.unit_name = unit_name
			kpi.is_visible_to_project = visible_to_project
			kpi.save()
			
			set_message(request, u"แก้ไขตัวชี้วัดเรียบร้อย")
			return redirect('view_administer_kpi')
		
	else:
		form = ModifyKPIForm(initial={'kpi_id':kpi.id, 'ref_no':kpi.ref_no, 'name':kpi.name, 'category':kpi.category, 'unit_name':kpi.unit_name, 'visible_to_project':kpi.is_visible_to_project})
	
	return render_response(request, "page_admin/administer_kpi_modify.html", {'kpi':kpi, 'form':form, 'has_categories':True})

@login_required
def view_administer_kpi_delete(request, kpi_id):
	if not request.user.is_superuser: return access_denied(request)
	
	kpi = KPI.objects.get(pk=kpi_id)
	
	if not KPISchedule.objects.filter(kpi=kpi).count():
		kpi.delete()
		set_message(request, u"ลบตัวชี้วัดเรียบร้อย")
	else:
		set_message(request, u"ไม่สามารถลบตัวชี้วัดนี้ได้ เนื่องจากยังมีการใช้งานอยู่")
	
	return redirect('view_administer_kpi')

@login_required
def view_administer_kpi_category(request):
	if not request.user.is_superuser: return access_denied(request)
	
	kpi_categories = KPICategory.objects.all()
	
	for kpi_category in kpi_categories:
		kpi_category.has_child = KPI.objects.filter(category=kpi_category).count() > 0
	
	return render_response(request, "page_admin/administer_kpi_category.html", {'kpi_categories':kpi_categories})

@login_required
def view_administer_kpi_category_add(request):
	if not request.user.is_superuser: return access_denied(request)
	
	if request.method == 'POST':
		form = ModifyKPICategoryForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			
			kpi = KPICategory.objects.create(name=name)
			
			set_message(request, u"สร้างประเภทตัวชี้วัดเรียบร้อย")
			return redirect('view_administer_kpi_category')
		
	else:
		form = ModifyKPICategoryForm()
	
	return render_response(request, "page_admin/administer_kpi_category_modify.html", {'form':form})

@login_required
def view_administer_kpi_category_edit(request, category_id):
	if not request.user.is_superuser: return access_denied(request)
	
	kpi_category = KPICategory.objects.get(pk=category_id)
	
	if request.method == 'POST':
		form = ModifyKPICategoryForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			
			kpi_category.name = name
			kpi_category.save()
			
			set_message(request, u"แก้ไขประเภทตัวชี้วัดเรียบร้อย")
			return redirect('view_administer_kpi_category')
		
	else:
		form = ModifyKPICategoryForm(initial={'name':kpi_category.name})
	
	return render_response(request, "page_admin/administer_kpi_category_modify.html", {'kpi_category':kpi_category, 'form':form})

@login_required
def view_administer_kpi_category_delete(request, category_id):
	if not request.user.is_superuser: return access_denied(request)
	
	kpi_category = KPICategory.objects.get(pk=category_id)
	
	if not KPI.objects.filter(category=kpi_category).count():
		kpi_category.delete()
		set_message(request, u"ลบประเภทตัวชี้วัดเรียบร้อย")
	else:
		set_message(request, u"ไม่สามารถลบประเภทตัวชี้วัดได้ เนื่องจากยังมีตัวชี้วัดที่ใช้ประเภทนี้อยู่")
	
	return redirect('view_administer_kpi_category')
