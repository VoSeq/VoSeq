import sys

from .base import *

PHOTOS_REPOSITORY = "local"

print('Testing')

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test.db',
    }
}
