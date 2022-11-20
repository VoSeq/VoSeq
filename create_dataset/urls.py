from django.urls import path

from . import views

app_name = 'create_dataset'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^results/$', views.generate_results, name='generate-dataset-results'),
    path(r'^results/(?P<dataset_id>[0-9]+)/$', views.results, name='create-dataset-results'),
    path(r'^download/(?P<dataset_id>[0-9]+)/$', views.serve_file, name='download-dataset-results'),
]
