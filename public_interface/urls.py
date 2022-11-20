from django.urls import path

from . import views


app_name = 'public_interface'

urlpatterns = [
    path('', views.index, name='index'),
    path('browse/', views.browse, name='browse'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('search/', views.search, name='simple_search'),
    path('search/advanced/', views.search_advanced, name='advanced_search'),
    path('p/<voucher_code>/', views.show_voucher, name='show_voucher'),
    path('s/<voucher_code>/<gene_code>/', views.show_sequence, name='show_sequence'),

    # for admin purposes
    path('admin/public_interface/vouchers/batch_changes/ids=<selected>/', views.change_selected, name='change_selected'),
]
