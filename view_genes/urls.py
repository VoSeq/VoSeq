from django.urls import path

from . import views


app_name = 'view_genes'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^(?P<gene_code>.+)/$', views.gene, name='gene'),
]
