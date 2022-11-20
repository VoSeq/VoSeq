from django.urls import path

from . import views


app_name = 'voucher_table'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^results/$', views.results, name='results'),
]
