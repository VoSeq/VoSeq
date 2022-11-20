from django.urls import path

from . import views


app_name = 'overview_table'
urlpatterns = [
    path(r'^$', views.index, name='index'),
]
