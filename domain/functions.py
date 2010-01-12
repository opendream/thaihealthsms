from datetime import datetime, date, timedelta

from django.db.models import Max

from models import KPISubmission, FinanceKPISubmission

# KPI
def get_current_and_last_submission(target_project):
	current_date = date.today()
	
	currents = KPISubmission.objects.filter(target=target_project, start_date__lte=current_date, end_date__gte=current_date)
	
	latest_date = KPISubmission.objects.filter(target=target_project, end_date__lt=current_date).aggregate(Max('end_date'))['end_date__max']
	latests = KPISubmission.objects.filter(target=target_project, end_date=latest_date)
	
	return (currents, latests)

def get_current_and_last_finance_submission(project):
	current_date = date.today()
	
	currents = FinanceKPISubmission.objects.filter(project=project, start_date__lte=current_date, end_date__gte=current_date)
	
	latest_date = FinanceKPISubmission.objects.filter(project=project, end_date__lt=current_date).aggregate(Max('end_date'))['end_date__max']
	latests = FinanceKPISubmission.objects.filter(project=project, end_date=latest_date)
	
	return (currents, latests)