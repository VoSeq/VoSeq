from django.urls import path

from . import views


app_name = 'gbif'
urlpatterns = [
    path('', views.index, name='index'),
    path('dump_data/', views.dump_data, name='dump_data'),
]
