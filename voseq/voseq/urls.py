from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^create_gene_table', include('gene_table.urls', namespace='gene_table')),
    url(r'^create_voucher_table', include('voucher_table.urls', namespace='voucher_table')),
    url(r'^create_dataset', include('create_dataset.urls', namespace='create_dataset')),
    url(r'^genbank_fasta', include('genbank_fasta.urls', namespace='genbank_fasta')),
    url(r'^blast_local', include('blast_local.urls', namespace='blast_local')),
    url(r'^blast_local_full', include('blast_local_full.urls', namespace='blast_local_full')),
    url(r'^blast_ncbi', include('blast_ncbi.urls', namespace='blast_ncbi')),
    url(r'^blast_new', include('blast_new.urls', namespace='blast_new')),
    url(r'^view_table', include('overview_table.urls', namespace='view_table')),
    url(r'^genes', include('view_genes.urls', namespace='view_genes')),
    url(r'^share_data_gbif', include('gbif.urls', namespace='gbif')),
    url(r'^', include('public_interface.urls', namespace='public_interace')),

    url(r'^admin/', include(admin.site.urls)),

    # user auth urls
    url(r'^accounts/', include('registration.backends.default.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
