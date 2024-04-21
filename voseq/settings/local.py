import json

from django.core.exceptions import ImproperlyConfigured

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

MANAGERS = ()

ADMINS = ()

SECRETS_FILE = os.path.join(BASE_DIR, '..', 'config.json')

with open(SECRETS_FILE) as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


BASE_URL = get_secret("BASE_URL")
SECRET_KEY = get_secret("SECRET_KEY")

GOOGLE_MAPS_API_KEY = get_secret("GOOGLE_MAPS_API_KEY")

PHOTOS_REPOSITORY = get_secret("PHOTOS_REPOSITORY")
if PHOTOS_REPOSITORY == 'flickr':
    FLICKR_API_KEY = get_secret("FLICKR_API_KEY")
    FLICKR_API_SECRET = get_secret("FLICKR_API_SECRET")

ELASTICSEARCH = False


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'voseq',
        'USER': 'carlosp420',
        'PASSWORD': get_secret('DB_PASS'),
        'HOST': 'localhost',
        'PORT': get_secret('DB_PORT'),
    }
}

INSTALLED_APPS += ('debug_toolbar',)

DB_NAME = get_secret("DB_NAME")

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': '{}_haystack'.format(DB_NAME),
        'INCLUDE_SPELLING': True,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.AdvancedSearchIndex',
            'public_interface.search_indexes.AutoCompleteIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'autocomplete': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': '{}_autocomplete'.format(DB_NAME),
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'vouchers': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': '{}_vouchers'.format(DB_NAME),
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.AdvancedSearchIndex',
            'public_interface.search_indexes.AutoCompleteIndex',
        ],
    },
    'advanced_search': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': '{}_advanced_search'.format(DB_NAME),
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
}
HAYSTACK_DEFAULT_OPERATOR = 'AND'
# HAYSTACK_IDENTIFIER_METHOD = 'public_interface.models.get_identifier'

if DEBUG is True:
    INTERNAL_IPS = ["127.0.0.1"]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_secret("EMAIL_HOST")
EMAIL_PORT = get_secret("EMAIL_PORT")
EMAIL_HOST_USER = get_secret("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = get_secret("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = get_secret("EMAIL_USE_TLS")
