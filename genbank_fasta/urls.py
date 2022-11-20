from django.urls import path

from . import views


app_name = 'genbank_fasta'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.generate_results, name='generate-genbank-fasta-results'),
    path('results/(<dataset_id>)/', views.results, name='create-genbank-results'),
    path('download/(<dataset_id>)/', views.serve_file, name='download-genbank-fasta-results'),
]
