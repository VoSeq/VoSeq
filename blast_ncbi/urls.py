from django.urls import path

from . import views


app_name = 'blast_local_ncbi'
urlpatterns = [
    path('<voucher_code>/<gene_code>/', views.index, name='index'),
]
