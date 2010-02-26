from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect

from accounts.models import UserRoleResponsibility
from comments.models import Comment
from domain.models import MasterPlan, Project

from comments import functions as comment_functions
from report import functions as report_functions

from helper import utilities
from helper.shortcuts import render_response

def view_frontpage(request):
	if not request.user.is_authenticated():
		return redirect("/accounts/login/")
	
	else:
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
		
		raise Http404

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
		project.reports = report_functions.get_checkup_reports(project)
		
	return render_response(request, "page_dashboard/dashboard_sector_assistant.html", {'projects':projects})

def _view_project_manager_frontpage(request):
	responsibility = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name='project_manager')
	project = responsibility[0].projects.all()[0]
	return redirect("/project/%d/" % project.id)

def _view_project_manager_assistant_frontpage(request):
	responsibility = UserRoleResponsibility.objects.filter(user=request.user.get_profile(), role__name="project_manager_assistant")
	project = responsibility[0].projects.all()[0]
	return redirect("/project/%d/" % project.id)

@login_required
def view_dashboard_my_projects(request):
	if utilities.user_has_role(request.user, 'sector_manager_assistant'):
		if request.method == 'POST':
			projects = request.POST.getlist('project')
			
			responsibility = UserRoleResponsibility.objects.get(user=request.user.get_profile())
			
			responsibility.projects.clear()
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

			return render_response(request, "page_dashboard/dashboard_sector_assistant_projects.html", {'master_plans':master_plans})
	else:
		return redirect('view_frontpage')

def _responsible_this_project(project, my_projects):
	for my_project in my_projects:
		if my_project.id == project.id:
			return True

	return False
