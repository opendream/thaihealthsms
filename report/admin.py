from django.contrib import admin

from models import *

admin.site.register(Report)
admin.site.register(ReportProject)
admin.site.register(ReportSchedule)
admin.site.register(ReportScheduleTextResponse)
admin.site.register(ReportScheduleFileResponse)
