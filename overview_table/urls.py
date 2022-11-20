from django.urls import path

from . import views


app_name = 'overview_table'
urlpatterns = [
    path('', views.index, name='index'),
]
