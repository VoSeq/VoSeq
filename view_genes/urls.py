from django.urls import path

from . import views


app_name = 'view_genes'
urlpatterns = [
    path('', views.index, name='index'),
    path('(<gene_code>)/', views.gene, name='gene'),
]
