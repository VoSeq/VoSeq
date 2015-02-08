from django.conf.urls import patterns
from django.conf.urls import url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^browse/$', views.browse, name='browse'),
    url(r'^search/$', views.search, name='search'),
    # url(r'^search/', include('haystack.urls')),
    url(r'^p/(?P<voucher_code>.+)/$', views.show_voucher, name='show_voucher'),
    url(r'^s/(?P<voucher_code>.+)/(?P<gene_code>.+)/$', views.show_sequence, name='show_sequence'),
                       
    # for admin purposes
    url(r'^admin/public_interface/vouchers/batch_changes/ids=(?P<selected>[CP\d+\-\d+\,*]*)/$', views.change_selected, name='change_selected'),
)
