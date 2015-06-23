from django.conf.urls import patterns
from django.conf.urls import url

from . import views


urlpatterns = patterns(
    '',
    url(r'^/$', views.index, name='index'),
    url(r'^/dump_data/$', views.dump_data, name='dump_data'),
)
