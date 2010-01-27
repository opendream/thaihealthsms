from domain.models import UserAccount

def user_post_save_callback(sender, instance, created, *args, **kwargs):
	if created: UserAccount.objects.create(user=instance)

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import simplejson
from domain.models import Sector, MasterPlan, Project

@login_required
def ajax_list_master_plans(request):
	master_plans = MasterPlan.objects.all()
	
	object_list = list()
	for master_plan in master_plans:
		object_list.append({'id':master_plan.id, 'ref_no':master_plan.ref_no, 'name':master_plan.name})
	
	return HttpResponse(simplejson.dumps(object_list))

@login_required
def ajax_list_projects(request):
	master_plan_id = request.GET['master_plan_id']
	
	if master_plan_id:
		projects = Project.objects.filter(master_plan=MasterPlan(id=master_plan_id), parent_project=None)
		
		object_list = list()
		for project in projects:
			object_list.append({'id':project.id, 'ref_no':project.ref_no, 'name':project.name})
		
		return HttpResponse(simplejson.dumps(object_list))
	else:
		return HttpResponse('')

