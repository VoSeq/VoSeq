from django.conf.urls import url

from .views import public_views as views
from .views import admin_views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^vouchers/add/$', admin_views.add_voucher, name='add_voucher'),
    url(r'^vouchers/add/(?P<code>\w+)/?$',admin_views.add_voucher, name='add_voucher'),

    url(r'^vouchers/upload/$', admin_views.upload_vouchers, name='upload_vouchers'),

    url(r'^sequences/add/$', admin_views.add_sequence, name='add_sequence'),
    url(r'^sequences/add/(?P<sequence_id>\d+)/$', admin_views.add_sequence, name='add_sequence'),

    url(r'^genes/add/$', admin_views.add_gene, name='add_gene'),

    url(r'^browse/$', views.browse, name='browse'),
    url(r'^autocomplete/$', views.autocomplete, name='autocomplete'),
    url(r'^search/$', views.search, name='simple_search'),
    url(r'^search/advanced/$', views.search_advanced, name='advanced_search'),
    url(r'^p/(?P<voucher_code>.+)/$', views.show_voucher, name='show_voucher'),
    url(r'^s/(?P<sequence_id>\d+)/$', views.show_sequence, name='show_sequence'),

    # for admin purposes
    url(r'^admin/public_interface/vouchers/batch_changes/ids=(?P<selected>.+)/$', views.change_selected, name='change_selected'),
]
