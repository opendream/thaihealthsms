import os
_base = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# ADMINS data will be used to create first group of admin account
# (every user will have 'Administration' as their firstname, without lastname.
# This firstname and lastname can be changed later)
ADMINS = (
	#('admin', 'application.testbed@gmail.com'),
	('panuta', 'panuta@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'postgresql_psycopg2'   		# 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'sms_dev' 			# Or path to database file if using sqlite3.
DATABASE_USER = 'sms_dev' 			# Not used with sqlite3.
DATABASE_PASSWORD = 'sms_dev' 		# Not used with sqlite3.
DATABASE_HOST = '' 			# Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = '' 			# Set to empty string for default. Not used with sqlite3.

ugettext = lambda s: s
LANGUAGES = (
	('th', ugettext('Thai')),
	#('en', ugettext('English')),
)

TIME_ZONE = 'Asia/Bangkok'
LANGUAGE_CODE = 'th'
SITE_ID = 1
USE_I18N = True

MEDIA_ROOT = os.path.join(_base, "media") + "/"
MEDIA_URL = '/m'


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'q398#=4j6xnjd_0v1r1lvi!5yae5@pst)-&q7r*1o#wq9hy#74'

TEMPLATE_CONTEXT_PROCESSORS = (
"django.core.context_processors.auth",
"django.core.context_processors.debug",
"django.core.context_processors.i18n",
"django.core.context_processors.media",
"thaihealthsms.context_processors.user_account",
"thaihealthsms.context_processors.messages",
)

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.load_template_source',
	'django.template.loaders.app_directories.load_template_source',
# 	'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.locale.LocaleMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'thaihealthsms.middleware.AJAXSimpleExceptionResponse',
)

ROOT_URLCONF = 'thaihealthsms.urls'

TEMPLATE_DIRS = (
	os.path.join(_base, "templates"),
)

#WEBSITE_ADDRESS = 'sms.thaihealth.or.th'
WEBSITE_ADDRESS = 'sms.opendream.in.th'

AUTH_PROFILE_MODULE = 'accounts.UserAccount'
ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = "/dashboard/"

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'application.testbed@gmail.com'
EMAIL_HOST_PASSWORD = 'opendream'
EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = '[SMS] '


SYSTEM_NOREPLY_EMAIL = EMAIL_HOST_USER

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'registration',
	'thaihealthsms.accounts',
	'thaihealthsms.administer',
	'thaihealthsms.comments',
	'thaihealthsms.dashboard',
	'thaihealthsms.domain',
	'thaihealthsms.finance',
	'thaihealthsms.interface',
	'thaihealthsms.helper',
	'thaihealthsms.kpi',
	'thaihealthsms.report',
)

# ===== SMS Settings ===== #

SYSTEM_NAME = 'Thai Health Strategy Management Systems'

# Report Submitted File
REPORT_SUBMIT_FILE_PATH = os.path.join(_base, "media/report")
REPORT_SUBMIT_FILE_URL = "/m/report/"

# Report Notification
REPORT_ALERT_AFTER = 3

# Finance Schedule Notification
FINANCE_ALERT_BEFORE = 30
FINANCE_ALERT_AFTER = 7
