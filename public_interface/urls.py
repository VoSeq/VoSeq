from django.urls import path

from . import views


app_name = 'public_interface'

urlpatterns = [
    path(r'^$', views.index, name='index'),
    path(r'^browse/$', views.browse, name='browse'),
    path(r'^autocomplete/$', views.autocomplete, name='autocomplete'),
    path(r'^search/$', views.search, name='simple_search'),
    path(r'^search/advanced/$', views.search_advanced, name='advanced_search'),
    path(r'^p/(?P<voucher_code>.+)/$', views.show_voucher, name='show_voucher'),
    path(r'^s/(?P<voucher_code>.+)/(?P<gene_code>.+)/$', views.show_sequence, name='show_sequence'),

    # for admin purposes
    path(r'^admin/public_interface/vouchers/batch_changes/ids=(?P<selected>.+)/$', views.change_selected, name='change_selected'),
]
