"""
Django settings for voseq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import platform

from kombu import Exchange, Queue

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# replace with any name if you have more than one installation. This name will
# be used to generate the log filenames
APP_NAME = "voseq"

DEBUG = True

MANAGERS = ()
ADMINS = ()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# insdb.lepdb.net
# nymphalidae.lepdb.net
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'app', 'lepdb.net', 'nymphalidae.lepdb.net']

# for testing in Travis CI
TRAVIS = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_extensions',
    'registration',

    'haystack',
    'crispy_forms',

    # my apps
    'core',
    'public_interface',
    'create_dataset',
    'blast_local',
    'blast_local_full',
    'blast_ncbi',
    'blast_new',
    'stats',
    'view_genes',
    'genbank_fasta',
    'gene_table',
    'voucher_table',
    'gbif',
    'overview_table',

    'easy_thumbnails',
    'import_export',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'public_interface/templates/registration',
            'core/templates',
            'public_interface/templates/public_interface',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
            'debug': False,
        }
    },
]

SIMPLE_LOG_FORMAT = '%(levelname)s %(message)s'
VERBOSE_LOG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(threadName)s] ' \
                     '[%(name)s] [%(lineno)d] %(message)s'
LOG_DIR = '/tmp/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': VERBOSE_LOG_FORMAT
        },
        'simple': {
            'format': SIMPLE_LOG_FORMAT
        },
    },

    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },

    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'terminal': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + APP_NAME + '_main.log',
            'formatter': 'verbose',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOG_DIR + APP_NAME + '_main.debug.log',
            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['terminal', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'blast_local': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'blast_local_full': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'blast_ncbi': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'blast_new': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'core': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'create_dataset': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'gbif': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'genbank_fasta': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'gene_table': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'overview_table': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'public_interface': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'stats': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'view_genes': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
        'voucher_table': {
            'handlers': ['terminal', 'file', 'file_debug', 'mail_admins'],
            'level': 'DEBUG',
        },
    },
}
ROOT_URLCONF = 'voseq.urls'

WSGI_APPLICATION = 'voseq.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CRISPY_TEMPLATE_PACK = 'uni_form'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
MEDIA_ROOT = BASE_DIR + '/../run/media/'

MEDIA_URL = '/media/'

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    BASE_DIR,
    os.path.join(BASE_DIR, '..', 'public_interface'),
    os.path.join(BASE_DIR, '..', 'create_dataset'),
)

THUMBNAIL_ALIASES = {
    '': {
        'thumb': {'size': (200, 200), 'crop': False},
    },
}
# Get your API key from here:
# https://developers.google.com/maps/documentation/javascript/tutorial#api_key
# so that you can show Google Maps in your voucher pages.
GOOGLE_MAPS_API_KEY = 'fake api key'

FLICKR_API_KEY = "fake api key"
FLICKR_API_SECRET = "fake api secret"


# This VoSeq version
def get_version():
    import voseq
    return voseq.__version__


VERSION = get_version()

TESTING = False

# Django registration redux
# One-week activation window; you may, of course, use a different value.
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_AUTO_LOGIN = True  # Automatically log the user in.
SITE_ID = 1
LOGIN_REDIRECT_URL = '/browse/'

# Change this after obtaining VoSeq and before deployments to production server
SECRET_KEY = 'test_key'

# assume we dont run on windows
if 'Darwin' in platform.platform():
    OS = 'mac'
else:
    OS = 'linux'

BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

default_exchange = Exchange('default', type='direct')
CELERY_QUEUES = (
    Queue('default', default_exchange, routing_key='default'),
)
CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'

ASYNC_MODE = False
