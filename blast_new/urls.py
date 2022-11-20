from django.urls import path

from . import views


app_name = 'blast_local_new'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
]
