# Django settings for starfish project.


import os
import json

from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR) + os.sep + "Starfish-master"

# JSON-based secrets
secrets = json.load(open(os.path.join(PROJECT_ROOT, "secrets.json")))

def get_secret(setting, secrets=secrets):
    """Get the secret variable or return explicit exception."""
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

SEARCH_SETTINGS = {
    'syntax': {
        "DELIM": "|", # Delimeter of tokens
        "PERSON": "@", # Start of person token
        "TAG": "#", # Start of tag token
        "LITERAL": "\"", # Start of literal group (ignores DELIM, PERSON and TAG)
        "ESCAPE": "\\" # Symbol to indicate the next symbol is a normal symbol
    },
    'allowPartialPersonHandles': True,
    'alwaysIncludeMentionedPersons': True
}

HOSTNAME = 'starfish.innovatievooronderwijs.nl'
ADMIN_NOTIFICATION_EMAIL = get_secret("ADMIN_NOTIFICATION_EMAIL")
TAG_REQUEST_MESSAGE = "One or more used tags are not (yet) added. A moderator has been notified."
ACCOUNT_UPDATED_MSG = "Your {} has been updated successfully."
ITEM_UPDATED_MSG = "{} updated successfully."

QUESTION_ASKED_TEXT = "{author} asked the following question: '{title}'\n" + \
                      "It can be found at {questionlink}. The original " + \
                      "item can be found at {itemlink}."
COMMENT_PLACED_TEXT = "{author} commented on {itemlink}"

DEBUG = True

SERVER_EMAIL = get_secret("SERVER_EMAIL")
ADMINS = (get_secret("ADMIN_EMAIL")
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql',
        #'NAME': get_secret('DB_NAME'),
        #'USER': get_secret('DB_USER'),
        #'PASSWORD': get_secret('DB_PWD'),
        #'HOST': '',
        #'PORT': get_secret('DB_PORT'),
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*', '83.96.200.111', '127.0.0.1']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/www/Starfish/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = get_secret("SECRET_KEY")


# template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS' : True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'steep.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'steep.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'search',
	'dashboard',
    'widget_tweaks',
    'bootstrap3_datetime',
    'ckeditor',
    'ckeditor_uploader',
)

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
   'default': {
       'toolbar_Full': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
            ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
            ['NumberedList','BulletedList'],
            ['Indent','Outdent'],
            ['Maximize'],
        ],
   },
}

SERIALIZATION_MODULES = {'json-unicode': 'serializers.json_unicode'}

# Logging performed by this configuration is to send an email
# to the site admins on every HTTP 500 error when DEBUG=False.
# If DEBUG=True, messages will be written to console. See
# http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'search': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL='/'

ITEM_TYPES = (
              ('G', 'Good Practice'),
              ('R', 'Project'),
              ('E', 'Event'),
              ('S', 'Glossary'),
              ('I', 'Information'),
              ('P', 'Person'),
              ('Q', 'Question'),
              ('U', 'User Case'),
              )

IVOAUTH_TOKEN = get_secret("IVO_TOKEN")
IVOAUTH_URL = "https://auth.innovatievooronderwijs.nl"
AUTHENTICATION_BACKENDS = (
            'search.auth_backend.EmailBackend',
            #'search.auth_backend.PasswordlessAuthBackend',
)
