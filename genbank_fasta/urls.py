from django.urls import path

from . import views


app_name = 'genbank_fasta'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^results/$', views.generate_results, name='generate-genbank-fasta-results'),
    path(r'^results/(?P<dataset_id>[0-9]+)/$', views.results, name='create-genbank-results'),
    path(r'^download/(?P<dataset_id>[0-9]+)/$', views.serve_file, name='download-genbank-fasta-results'),
]
