from django.urls import path

from . import views

app_name = 'create_dataset'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.generate_results, name='generate-dataset-results'),
    path('results/(<dataset_id>[0-9])/', views.results, name='create-dataset-results'),
    path('download/(<dataset_id>[0-9])/', views.serve_file, name='download-dataset-results'),
]
