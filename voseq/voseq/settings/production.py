from .local import *

# you need to specify a public folder your your statics files during deployment
STATIC_ROOT = "/var/www/VoSeq/static/"
MEDIA_ROOT = "/var/www/VoSeq/media/"


DEBUG = False
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = [
    '33.33.33.10',  # Your Domain or IP address
]
