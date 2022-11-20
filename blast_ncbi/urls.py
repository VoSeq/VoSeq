from django.urls import path

from . import views


app_name = 'blast_local_ncbi'
urlpatterns = [
    path(r'^(?P<voucher_code>.+)/(?P<gene_code>.+)/$', views.index, name='index'),
]
