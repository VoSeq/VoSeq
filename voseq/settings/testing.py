import sys

from .base import *

PHOTOS_REPOSITORY = "local"
ELASTICSEARCH = False

print('Testing')

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'


os.environ["TRAVIS"] = "True"
if 'TRAVIS' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE':   'django.db.backends.postgresql_psycopg2',
            'NAME':     'travis_ci_test',
            'USER':     'carlosp420',
            'PASSWORD': '',
            'HOST':     'localhost',
            'PORT':     '5432',
        }
    }
    DB_NAME = "travis_ci_test"
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test.db',
        }
    }
    DB_NAME = "test"


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
