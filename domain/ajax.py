from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson

from domain.models import Sector, MasterPlan, Project, Activity

@login_required
def ajax_list_master_plans(request):
	master_plans = MasterPlan.objects.all().order_by('ref_no')
	
	object_list = list()
	for master_plan in master_plans:
		object_list.append({'id':master_plan.id, 'ref_no':master_plan.ref_no, 'name':master_plan.name})
	
	return HttpResponse(simplejson.dumps(object_list))

@login_required
def ajax_list_projects(request):
	master_plan_id = request.GET['master_plan_id']
	
	if master_plan_id:
		projects = Project.objects.filter(master_plan=MasterPlan(id=master_plan_id), parent_project=None).order_by('ref_no')
		
		object_list = list()
		for project in projects:
			object_list.append({'id':project.id, 'ref_no':project.ref_no, 'name':project.name})
		
		return HttpResponse(simplejson.dumps(object_list))
	else:
		return HttpResponse('')

@login_required
def ajax_list_project_activities(request):
	project_id = request.GET.get('project_id')
	project = Project.objects.get(pk=project_id)
	
	activities = Activity.objects.filter(project=project)
	
	activity_list = []
	for activity in activities:
		if activity.start_date and activity.end_date:
			activity_list.append({'id':activity.id, 'name':activity.name, 'sy':activity.start_date.year, 'sm':activity.start_date.month, 'sd':activity.start_date.day, 'ey':activity.end_date.year, 'em':activity.end_date.month, 'ed':activity.end_date.day})
		else:
			activity_list.append({'id':activity.id, 'name':activity.name, 'sy':0, 'sm':0, 'sd':0, 'ey':0, 'em':0, 'ed':0})
	
	return HttpResponse(simplejson.dumps(activity_list))
	
		
	
	