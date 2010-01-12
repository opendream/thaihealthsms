# -*- encoding: utf-8 -*-

from django import template

from domain.constants import PROJECT_TYPE_TEXT
from domain.models import Project, UserAccount
from thaihealthsms.helper.utilities import format_date
from comments.models import CommentReceiver

register = template.Library()

#
# UNREAD COMMENTS
#
@register.simple_tag
def get_unread_comments(user_account_id):
	return CommentReceiver.objects.filter(receiver=UserAccount(id=user_account_id), is_read=False).count()

#
# TEMPLATE HEADER TAGS
#

@register.simple_tag
def print_project_header(project):
	html = '<div class="sector"><a href="/sector/' + str(project.sector.id) + '/">' + project.sector.name + '</a> - <a href="/master_plan/' + str(project.master_plan.id) + '/">' + project.master_plan.name + '</a></div>'
	
	if not project.parent_project:
		html += '<div class="title"><span> ' + unicode(PROJECT_TYPE_TEXT[project.type], "utf-8") + ' ' + project.ref_no + '</span> ' + project.name + '</div>'
		html += unicode('<div class="info"><span>รับผิดชอบโดย ', "utf-8") + project.manager.first_name + ' ' + project.manager.last_name + unicode('</span> <a href="#" class="post-comment">ความคิดเห็น &#187; แผนงาน</a></div>', "utf-8")
	
	else:
		html += '<div class="parent"><a href="/program/' + str(project.parent_project.id) + '/">' + project.parent_project.name + '</a></div>'
		html += '<div class="title"><span> ' + unicode(PROJECT_TYPE_TEXT[project.type], "utf-8") + ' ' + project.ref_no + '</span> ' + project.name + '</div>'
		html += unicode('<div class="info"><span>รับผิดชอบโดย ', "utf-8") + project.manager.first_name + ' ' + project.manager.last_name + unicode('</span> <a href="#" class="post-comment">ความคิดเห็น &#187; โครงการ</a></div>', "utf-8")
	
	return html

@register.simple_tag
def print_activity_header(activity):
	html = '<div class="sector"><a href="/sector/' + str(activity.project.sector.id) + '/">' + activity.project.sector.name + '</a> - <a href="/master_plan/' + str(activity.project.master_plan.id) + '/">' + activity.project.master_plan.name + '</a></div>'
	
	if activity.project.parent_project:
		html += '<div class="parent"><a href="/program/' + str(activity.project.parent_project.id) + '/">' + activity.project.parent_project.name + '</a> &#187; <a href="/project/' + str(activity.project.id) + '/">' + activity.project.name + '</a></div>'
		
	else:
		html += '<a href="/project/' + str(activity.project.id) + '/">' + activity.project.name + '</a> &#187;</div>'
	
	html += unicode('<div class="title"><span>กิจกรรม</span> ', "utf-8") + activity.name + '</div>'
	html += unicode('<div class="info"><a href="#" class="post-comment">ความคิดเห็น &#187; กิจกรรม</a></div>', "utf-8")
	
	return html

@register.simple_tag
def print_report_header(report_schedule):
	html = '<div class="sector"><a href="/sector/' + str(report_schedule.report_project.project.sector.id) + '/">' + report_schedule.report_project.project.sector.name + '</a> - <a href="/master_plan/' + str(report_schedule.report_project.project.master_plan.id) + '/">' + report_schedule.report_project.project.master_plan.name + '</a></div>'
	
	if report_schedule.report_project.project.parent_project:
		html += '<div class="parent"><a href="/program/' + str(report_schedule.report_project.project.parent_project.id) + '/">' + report_schedule.report_project.project.parent_project.name + '</a> &#187; <a href="/project/' + str(report_schedule.report_project.project.id) + '/">' + report_schedule.report_project.project.name + '</a> &#187;</div>'
		
	else:
		html += '<div class="parent"><a href="/program/' + str(report_schedule.report_project.project.id) + '/">' + report_schedule.report_project.project.name + '</a></div>'
	
	html += unicode('<div class="title"><span>รายงาน</span> ', "utf-8") + report_schedule.report_project.report.name + '</div>'
	html += unicode('<div class="info"><span>รอบกำหนดส่ง ', "utf-8") + format_date(report_schedule.due_date) + unicode('</span> <a href="#" class="post-comment">ความคิดเห็น &#187; รายงาน</a></div>', "utf-8")
	
	return html

#
# KPI
#
@register.simple_tag
def kpi_range_name(value):
	if value < 50: return "lowest"
	elif value < 100: return "low"
	elif value == 100: return "expect"
	else: return "above"
