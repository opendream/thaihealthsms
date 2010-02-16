from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(request, *args, **kwargs):
	kwargs['context_instance'] = RequestContext(request)
	return render_to_response(*args, **kwargs)

def access_denied(request):
	return render_response(request, 'system/access_denied.html')