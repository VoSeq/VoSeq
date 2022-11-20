from django.urls import path

from . import views


app_name = 'gbif'
urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^dump_data/$', views.dump_data, name='dump_data'),
]
