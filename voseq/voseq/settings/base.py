"""
Django settings for voseq project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/


ALLOWED_HOSTS = []

# for testing in Travis CI
TRAVIS = False

# Application definition

INSTALLED_APPS = (
    # added
    'suit',
    'haystack',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

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
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
)

ROOT_URLCONF = 'voseq.urls'

WSGI_APPLICATION = 'voseq.wsgi.application'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
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
        'INDEX_NAME': 'autocomplete',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'vouchers': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'vouchers',
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
        'INDEX_NAME': 'advanced_search',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
}
HAYSTACK_DEFAULT_OPERATOR = 'AND'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    BASE_DIR,
    os.path.join(BASE_DIR, '..', 'public_interface'),
)

# Get your API key from here:
# https://developers.google.com/maps/documentation/javascript/tutorial#api_key
# so that you can show Google Maps in your voucher pages.
GOOGLE_MAPS_API_KEY = 'fake api key'

# This VoSeq version
VERSION = '2.0.0'

TESTING = False

# Change this after obtaining VoSeq and before deployments to a production server
SECRET_KEY = '65~55UJd9BRyFq_ota{IxlG9w=2ZO3'
