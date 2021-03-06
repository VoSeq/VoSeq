from .local import *  # noqa

MEDIA_ROOT = '/data/media/'
STATIC_ROOT = '/data/static/'

DEBUG = False

DATABASES['default']['HOST'] = 'db'
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['NAME'] = get_secret('DB_NAME')
