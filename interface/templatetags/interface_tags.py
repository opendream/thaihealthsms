# -*- encoding: utf-8 -*-
from datetime import date

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from domain.constants import PROJECT_TYPE_TEXT
from accounts.models import UserAccount, UserRoleResponsibility
from comments.models import Comment, CommentReceiver, CommentReply, CommentReplyReceiver
from domain.models import Project

from thaihealthsms.helper import utilities

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

@register.simple_tag
def get_comment_count(user, object_name, object_id):
	return CommentReceiver.objects.filter(receiver=user.get_profile(), comment__object_name=object_name, comment__object_id=object_id).count() + CommentReplyReceiver.objects.filter(receiver=user.get_profile(), reply__comment__object_name=object_name, reply__comment__object_id=object_id).count()

#
# TEMPLATE HEADER TAGS
#

@register.simple_tag
def print_sector_header(sector):
	html = unicode('<div class="title"><span>สำนัก %d</span> %s</div>', 'utf-8') % (sector.ref_no, sector.name)
	
	managers = ', '.join([manager.first_name + ' ' + manager.last_name for manager in utilities.who_responsible(sector)])
	if not managers: managers = unicode('(ไม่มีผู้รับผิดชอบ)', 'utf-8')
	
	html += unicode('<div class="info">ผู้จัดการสำนัก: %s</div>', 'utf-8') % managers
	return html

@register.simple_tag
def print_master_plan_header(master_plan):
	html = unicode('<div class="sector"><a href="%s">สำนัก %d %s</a></div>', 'utf-8') % (reverse('view_sector_overview', args=[master_plan.sector.id]), master_plan.sector.ref_no, master_plan.sector.name)
	html += unicode('<div class="title"><span>แผน %d</span> %s</div>', 'utf-8') % (master_plan.ref_no, master_plan.name)
	return html

@register.simple_tag
def print_project_header(user, project):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (project.master_plan.sector.id, project.master_plan.sector.ref_no, project.master_plan.sector.name, project.master_plan.id, project.master_plan.ref_no, project.master_plan.name)
	
	if not project.parent_project:
		managers = ', '.join([manager.first_name + ' ' + manager.last_name for manager in utilities.who_responsible(project)])
		
		no_managers = False
		if not managers:
			no_managers = True
			managers = unicode('(ไม่มีข้อมูล)', 'utf-8')
		
		html += '<div class="title"><span>%s %s</span> %s</div>' % (unicode(PROJECT_TYPE_TEXT[project.prefix_name], "utf-8"), project.ref_no, project.name)
		html += unicode('<div class="info"><span>ผู้จัดการแผนงาน: %s</span></div>', 'utf-8') % managers
		
	else:
		html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (project.parent_project.id, project.parent_project.ref_no, project.parent_project.name)
		html += '<div class="title"><span>%s %s</span> %s</div>' % (unicode(PROJECT_TYPE_TEXT[project.prefix_name], "utf-8"), project.ref_no, project.name)
		
		if project.start_date and project.end_date:
			html += unicode('<div class="info"><span>ระยะเวลาโครงการ: %s - %s</span></div>', 'utf-8') % (utilities.format_abbr_date(project.start_date), utilities.format_abbr_date(project.end_date))
		else:
			html += unicode('<div class="info"><span>ระยะเวลาโครงการ: (ไม่กำหนด)</span></div>', 'utf-8')
		
	return html

@register.simple_tag
def print_activity_header(user, activity):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (activity.project.master_plan.sector.id, activity.project.master_plan.sector.ref_no, activity.project.master_plan.sector.name, activity.project.master_plan.id, activity.project.master_plan.ref_no, activity.project.master_plan.name)
	html += '<div class="parent"><a href="/project/%d/">%s %s</a> &#187; <a href="/project/%d/">%s %s</a></div>' % (activity.project.parent_project.id, activity.project.parent_project.ref_no, activity.project.parent_project.name, activity.project.id, activity.project.ref_no, activity.project.name)
	html += unicode('<div class="title"><span>กิจกรรม</span> ', 'utf-8') + activity.name + '</div>'
	
	if activity.start_date and activity.end_date:
		html += unicode('<div class="info"><span>ระยะเวลากิจกรรม: %s - %s</span></div>', 'utf-8') % (utilities.format_abbr_date(activity.start_date), utilities.format_abbr_date(activity.end_date))
	else:
		html += unicode('<div class="info"><span>ระยะเวลากิจกรรม: (ไม่กำหนด)</span></div>', 'utf-8')
	
	return html

@register.simple_tag
def print_report_header(user, report_schedule):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (report_schedule.report_project.project.master_plan.sector.id, report_schedule.report_project.project.master_plan.sector.ref_no, report_schedule.report_project.project.master_plan.sector.name, report_schedule.report_project.project.master_plan.id, report_schedule.report_project.project.master_plan.ref_no, report_schedule.report_project.project.master_plan.name)
	html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (report_schedule.report_project.project.id, report_schedule.report_project.project.ref_no, report_schedule.report_project.project.name)
	html += unicode('<div class="title"><span>รายงาน</span> %s</div>', 'utf-8') % report_schedule.report_project.report.name
	html += unicode('<div class="info"><span>งวดวันที่ %s</span></div>', 'utf-8') % (utilities.format_abbr_date(report_schedule.due_date))
	return html

@register.simple_tag
def print_kpi_header(user, kpi_schedule):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (kpi_schedule.project.master_plan.sector.id, kpi_schedule.project.master_plan.sector.ref_no, kpi_schedule.project.master_plan.sector.name, kpi_schedule.project.master_plan.id, kpi_schedule.project.master_plan.ref_no, kpi_schedule.project.master_plan.name)
	html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (kpi_schedule.project.id, kpi_schedule.project.ref_no, kpi_schedule.project.name)
	html += unicode('<div class="title"><span>ตัวชี้วัด</span> %s</div>', 'utf-8') % kpi_schedule.kpi.name
	html += unicode('<div class="info"><span>รอบวันที่ %s</span></div>', 'utf-8') % (utilities.format_abbr_date(kpi_schedule.target_on))
	return html

@register.simple_tag
def print_finance_header(user, finance_schedule):
	html = unicode('<div class="sector"><a href="/sector/%d/">สำนัก %d %s</a> - <a href="/master_plan/%d/">แผน %d %s</a></div>', 'utf-8') % (finance_schedule.project.master_plan.sector.id, finance_schedule.project.master_plan.sector.ref_no, finance_schedule.project.master_plan.sector.name, finance_schedule.project.master_plan.id, finance_schedule.project.master_plan.ref_no, finance_schedule.project.master_plan.name)
	html += '<div class="parent"><a href="/project/%s/">%s %s</a></div>' % (finance_schedule.project.id, finance_schedule.project.ref_no, finance_schedule.project.name)
	html += unicode('<div class="title">งวดเบิกจ่ายวันที่ %s</div>', 'utf-8') % utilities.format_abbr_date(finance_schedule.target_on)
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

#
# REPORT
#
@register.simple_tag
def display_report_status(report_schedule):
	from report.models import SUBMIT_ACTIVITY, APPROVE_ACTIVITY, REJECT_ACTIVITY
	if report_schedule.state == SUBMIT_ACTIVITY and report_schedule.report_project.report.need_approval:
		return '[รายงานกำลังรอการตรวจสอบ]'
	elif report_schedule.state == REJECT_ACTIVITY:
		return '[รายงานถูกตีกลับ]'
	
	return ''

#
# KPI
#
@register.simple_tag
def display_kpi_revision_html(revision):
	from thaihealthsms.helper.utilities import get_kpi_revision_html
	return get_kpi_revision_html(revision)

@register.simple_tag
def display_finance_revision_html(revision):
	from thaihealthsms.helper.utilities import get_finance_revision_html
	return get_finance_revision_html(revision)

@register.simple_tag
def display_finance_graph_class(target, result):
	if result < target:
		return 'low'
	else:
		return 'high'

@register.simple_tag
def display_kpi_graph_class(percentage):
	if percentage <= 40:
		return 'low'
	elif percentage <= 80:
		return 'medium'
	else:
		return 'high'

#
# COMMENT
#

@register.simple_tag
def display_project_comment_button(user, project):
	if not utilities.responsible(user, 'project_manager,project_manager_assistant', project.parent_project) and not user.is_superuser and utilities.who_responsible(project.parent_project):
		return unicode('<div class="comment"><a href="#" class="post-project-comment" rel="project/%d"><img src="%s/images/comment_add.png" class="icon"/> เขียนความคิดเห็น</a></div>', 'utf-8') % (project.id, settings.MEDIA_URL)
	return ''

@register.simple_tag
def display_activity_comment_button(user, activity):
	if not utilities.responsible(user, 'project_manager,project_manager_assistant', activity.project) and not user.is_superuser and utilities.who_responsible(activity.project.parent_project):
		return unicode('<div class="comment"><a href="#" class="post-activity-comment" rel="activity/%d"><img src="%s/images/comment_add.png" class="icon"/> เขียนความคิดเห็น</a></div>', 'utf-8') % (activity.id, settings.MEDIA_URL)
	return ''

@register.simple_tag
def display_report_comment_button(user, report_schedule):
	if not utilities.responsible(user, 'project_manager,project_manager_assistant', report_schedule.report_project.project) and not user.is_superuser and utilities.who_responsible(report_schedule.report_project.project):
		return unicode('<div class="comment"><a href="#" class="post-report-comment" rel="report/%d"><img src="%s/images/comment_add.png" class="icon"/> เขียนความคิดเห็น</a></div>', 'utf-8') % (report_schedule.id, settings.MEDIA_URL)
	return ''

@register.simple_tag
def display_kpi_comment_button(user, kpi_schedule):
	if not utilities.responsible(user, 'project_manager,project_manager_assistant', kpi_schedule.project) and not user.is_superuser and utilities.who_responsible(kpi_schedule.project):
		return unicode('<div class="comment"><a href="#" class="post-kpi-comment" rel="kpi/%d"><img src="%s/images/comment_add.png" class="icon"/> เขียนความคิดเห็น</a></div>', 'utf-8') % (kpi_schedule.id, settings.MEDIA_URL)
	return ''

@register.simple_tag
def display_finance_comment_button(user, finance_schedule):
	if not utilities.responsible(user, 'project_manager,project_manager_assistant', finance_schedule.project) and not user.is_superuser and utilities.who_responsible(finance_schedule.project):
		return unicode('<div class="comment"><a href="#" class="post-finance-comment" rel="finance/%d"><img src="%s/images/comment_add.png" class="icon"/> เขียนความคิดเห็น</a></div>', 'utf-8') % (finance_schedule.id, settings.MEDIA_URL)
	return ''

@register.simple_tag
def display_comment_object_title(object_name, object):
	if object_name == 'report':
		return unicode('[แผนงาน %s] %s งวดวันที่ %s', 'utf-8') % (object.report_project.project.ref_no, object.report_project.report.name, utilities.format_abbr_date(object.due_date))
	elif object_name == 'kpi':
		return unicode('[แผนงาน %s] ตัวชี้วัด %s งวดวันที่ %s', 'utf-8') % (object.project.ref_no, object.kpi.ref_no, utilities.format_abbr_date(object.target_on))
	elif object_name == 'finance':
		return unicode('[แผนงาน %s] การเบิกจ่ายงวดวันที่ %s', 'utf-8') % (object.project.ref_no, utilities.format_abbr_date(object.target_on))
	else:
		return unicode('[แผนงาน %s] %s', 'utf-8') % (object.ref_no, object.name)

@register.simple_tag
def generate_comment_html(comment):
	html = '<li class="' + ("read" if comment.is_read else "unread" ) + '" id="comment-%d">' % comment.id
	html += unicode('<div class="comment"><p>%s</p><div class="metadata"><span class="reply" id="reply-comment-box"><img src="%s/images/comment_reply.png" class="icon"/> <a href="#" id="comment-%d" class="reply-comment" title="ตอบกลับความคิดเห็น">ตอบกลับความคิดเห็น</a></span><span class="sender">%s %s</span> ส่งเมื่อวันที่ %s</div></div>', 'utf-8') % (comment.message, settings.MEDIA_URL, comment.id, comment.sent_by.first_name, comment.sent_by.last_name, utilities.format_abbr_datetime(comment.sent_on))
	html += '<ul class="replies">'
	
	for reply in comment.replies:
		html += '<li class="' + ("read" if reply.is_read else "unread" ) + '">'
		html += unicode('<p>%s</p><div class="metadata"><span class="sender">%s %s</span>ส่งเมื่อวันที่ %s</div></li>', 'utf-8') % (reply.content, reply.sent_by.first_name, reply.sent_by.last_name, utilities.format_abbr_datetime(reply.sent_on))
	
	html += '</ul></li>'
	
	return html
