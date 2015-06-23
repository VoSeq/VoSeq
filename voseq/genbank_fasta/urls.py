from django.conf.urls import patterns
from django.conf.urls import url

from . import views


urlpatterns = patterns(
    '',
    url(r'^/$', views.index, name='index'),
    url(r'^/results/$', views.results, name='results'),
    url(r'^/results/(?P<file_name>.+\.txt)/$', views.serve_file, name='serve_file'),
)
