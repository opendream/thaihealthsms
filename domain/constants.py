# -*- encoding: utf-8 -*-

from domain.models import Project

PROJECT_TYPE_TEXT = {
	Project.PROJECT_IS_PROGRAM:"แผนงาน",
	Project.PROJECT_IS_PROJECT:"โครงการ",
	Project.PROJECT_IS_SUB_PROJECT:"โครงการย่อย"
}
