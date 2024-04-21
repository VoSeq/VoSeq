from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from django.contrib import admin
from django.contrib.staticfiles import views

from create_dataset.urls import urlpatterns as create_dataset_urls
from gene_table.urls import urlpatterns as gene_table_urls
from voucher_table.urls import urlpatterns as voucher_table_urls
from genbank_fasta.urls import urlpatterns as genbank_fasta_urls
from blast_local.urls import urlpatterns as blast_local_urls
from blast_local_full.urls import urlpatterns as blast_local_full_urls
from blast_ncbi.urls import urlpatterns as blast_ncbi_urls
from blast_new.urls import urlpatterns as blast_new_urls
from overview_table.urls import urlpatterns as overview_table_urls
from view_genes.urls import urlpatterns as view_genes_urls
from gbif.urls import urlpatterns as gbif_urls
from public_interface.urls import urlpatterns as public_interface_urls


urlpatterns = [
    path('create_gene_table/', include(gene_table_urls)),
    path('create_voucher_table/', include(voucher_table_urls)),
    path('create_dataset/', include(create_dataset_urls)),
    path('genbank_fasta/', include(genbank_fasta_urls)),
    path('blast_local/', include(blast_local_urls)),
    path('blast_local_full/', include(blast_local_full_urls)),
    path('blast_ncbi/', include(blast_ncbi_urls)),
    path('blast_new/', include(blast_new_urls)),
    path('view_table/', include(overview_table_urls)),
    path('genes/', include(view_genes_urls)),
    path('share_data_gbif/', include(gbif_urls)),
    path('', include(public_interface_urls)),

    path('admin/', admin.site.urls),

    # user auth urls
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('registration.backends.default.urls')),
]
# ] + static(
#     settings.STATIC_URL,
#     document_root=settings.STATIC_ROOT,
# ) + static(
#     settings.MEDIA_URL,
#     document_root=settings.MEDIA_ROOT,
# )

if settings.DEBUG:
    urlpatterns += [
        path('media/<path>', views.serve)
    ]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
