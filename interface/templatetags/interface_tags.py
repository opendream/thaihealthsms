# -*- encoding: utf-8 -*-

from django import template
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from domain.constants import PROJECT_TYPE_TEXT
from domain.models import Project, UserAccount, UserRoleResponsibility
from thaihealthsms.helper.utilities import format_date
from thaihealthsms.helper.utilities import who_responsible
from comments.models import CommentReceiver, CommentReplyReceiver

register = template.Library()

#
# UNREAD COMMENTS
#
@register.simple_tag
def get_unread_comments(user_account_id):
	user_account = UserAccount(id=user_account_id)
	
	unread_count = CommentReceiver.objects.filter(receiver=user_account, is_read=False).count()\
		 + CommentReplyReceiver.objects.filter(receiver=user_account, is_read=False).count()
	
	return unread_count

#
# TEMPLATE HEADER TAGS
#

@register.simple_tag
def print_sector_header(sector):
	html = unicode('<div class="title"><span>สำนัก %d</span> %s</div>', 'utf-8') % (sector.ref_no, sector.name)
	
	managers = ', '.join([user.first_name + ' ' + user.last_name for user in who_responsible(sector)])
	html += unicode('<div class="info">ผู้จัดการสำนัก %s</div>', 'utf-8') % managers
	
	return html

@register.simple_tag
def print_master_plan_header(master_plan):
	html = unicode('<div class="sector"><a href="%s">สำนัก %d %s</a></div>', 'utf-8') % (reverse('view_sector_overview', args=[master_plan.sector.id]), master_plan.sector.ref_no, master_plan.sector.name)
	html += unicode('<div class="title"><span>แผน %d</span> %s</div>', 'utf-8') % (master_plan.ref_no, master_plan.name)
	
	return html

@register.simple_tag
def print_project_header(project):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (project.sector.id, project.sector.ref_no, project.sector.name, project.master_plan.id, project.master_plan.ref_no, project.master_plan.name)
	managers = ', '.join([user.first_name + ' ' + user.last_name for user in who_responsible(project)])
	
	if not project.parent_project:
		html += '<div class="title"><span>%s %s</span> %s</div>' % (unicode(PROJECT_TYPE_TEXT[project.prefix_name], "utf-8"), project.ref_no, project.name)
		html += ('<div class="info"><span>' + _('Responsible By') + ': %s</span><a href="#" class="post-project-comment" rel="project/' + str(project.id) + '">' + _('Submit a comment to manager') + '</a></div>') % managers
	
	else:
		html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (project.parent_project.id, project.parent_project.ref_no, project.parent_project.name)
		html += '<div class="title"><span>%s %s</span> %s</div>' % (unicode(PROJECT_TYPE_TEXT[project.prefix_name], "utf-8"), project.ref_no, project.name)
		html += ('<div class="info"><a href="#" class="post-project-comment" rel="project/' + str(project.id) + '">' + _('Comment') + ' &raquo; ' + _('Project') + '</a></div>')
	
	return html

@register.simple_tag
def print_activity_header(activity):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (activity.project.sector.id, activity.project.sector.ref_no, activity.project.sector.name, activity.project.master_plan.id, activity.project.master_plan.ref_no, activity.project.master_plan.name)
	
	html += '<div class="parent"><a href="/project/%d/">%s %s</a> &#187; <a href="/project/%d/">%s %s</a></div>' % (activity.project.parent_project.id, activity.project.parent_project.ref_no, activity.project.parent_project.name, activity.project.id, activity.project.ref_no, activity.project.name)
	
	html += '<div class="title"><span>' + _('Activity') + ':</span> ' + activity.name + '</div>'
	html += '<div class="info"><a href="#" class="post-activity-comment" rel="activity/' + str(activity.id) + '">' + _('Comment') + ' &raquo; ' + _('Activity') + '</a></div>'
	
	return html

@register.simple_tag
def print_report_header(report_schedule):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (report_schedule.report_project.project.sector.id, report_schedule.report_project.project.sector.ref_no, report_schedule.report_project.project.sector.name, report_schedule.report_project.project.master_plan.id, report_schedule.report_project.project.master_plan.ref_no, report_schedule.report_project.project.master_plan.name)
	
	html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (report_schedule.report_project.project.id, report_schedule.report_project.project.ref_no, report_schedule.report_project.project.name)
	
	html += ('<div class="title"><span>' + _('Report') + ':</span> %s</div>') % report_schedule.report_project.report.name
	html += ('<div class="info"><span>' + _('Due date') + ': %s</span><a href="#" class="post-report-comment" rel="report/' + str(report_schedule.id) + '">' + _('Comment') + ' &raquo; ' + _('Report') + '</a></div>') % format_date(report_schedule.due_date)
	
	return html

#
# PROJECT
#
@register.simple_tag
def project_prefix_name(project):
	return unicode(PROJECT_TYPE_TEXT[project.prefix_name], "utf-8")

#
# DISPLAY TAG
#
@register.simple_tag
def display_report_repeating(report):
	html = 'ส่งรายงานวันที่ %d ในทุกๆ %d เดือน' % (report.schedule_month_cycle, report.schedule_date_due)

