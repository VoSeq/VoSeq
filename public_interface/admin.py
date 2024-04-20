from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django import forms
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpRequest
from import_export.widgets import ForeignKeyWidget

from public_interface.models import FlickrImages, LocalImages, GeneSets, Genes, \
    TaxonSets, Sequences, Vouchers
from public_interface.views import change_selected
from public_interface.forms import SequencesAdminForm


class ImageInLine(admin.StackedInline):
    model = LocalImages
    fields = ['voucher_image']


class FlickImageInLine(admin.StackedInline):
    model = FlickrImages
    fields = ['image_file', 'voucher_image']


class BatchImportGenesResource(resources.ModelResource):
    class Meta:
        model = Genes
        import_id_fields = ('gene_code',)
        fields = (
            'gene_code', 'genetic_code', 'length', 'description',
            'reading_frame', 'notes', 'aligned', 'intron',
            'prot_code', 'gene_type',
        )


class BatchImportVouchersResource(resources.ModelResource):
    class Meta:
        model = Vouchers
        import_id_fields = ('code',)
        fields = ('code',
                  'flickr_photo_url',
                  'orden', 'superfamily', 'family', 'subfamily', 'tribe',
                  'subtribe', 'genus', 'species', 'subspecies', 'author',
                  'hostorg', 'type_species', 'country', 'specific_locality',
                  'collector', 'date_collection', 'date_collection_end',
                  'latitude', 'longitude', 'max_altitude', 'min_altitude',
                  'voucher_code', 'voucher', 'voucher_locality',
                  'determined_by', 'sex', 'extraction', 'extraction_tube',
                  'date_extraction', 'published_in', 'notes',
                  )

    def save_instance(self, instance, new, using_transactions, dry_run=False):
        if dry_run:
            if instance.latitude and not coordinate_validated(instance.latitude):
                raise Exception("Latitude is in wrong format: {!r}. "
                                "Use decimal point.".format(instance.latitude))
            if instance.longitude and not coordinate_validated(instance.longitude):
                raise Exception("Longitude is in wrong format: {!r}. "
                                "Use decimal point.".format(instance.latitude))
        else:
            instance.save()


def coordinate_validated(coord):
    """Sometimes user inputs coordinates with comma."""
    try:
        float(coord)
    except ValueError:
        return False
    except TypeError:
        return False
    return True


class BatchImportSequencesResource(resources.ModelResource):
    gene = fields.Field(
        column_name='gene',
        attribute='gene',
        widget=ForeignKeyWidget(Genes, 'gene_code'),
    )

    class Meta:
        model = Sequences
        import_id_fields = ('code', 'gene')
        fields = (
            'code', 'gene', 'accession', 'lab_person', 'genbank', 'notes',
            'sequences',
        )


# Customize what and the way you show it
class VouchersAdmin(ImportExportModelAdmin):
    # import_template_name = 'admin/public_interface/vouchers/batch_import.html'
    list_display = ['code', 'genus', 'species', 'sex', 'voucher', 'country', 'collector']
    ordering = ['code']
    search_fields = ['code', 'genus', 'species']

    actions = ['batch_changes']

    fieldsets = [('Voucher Information', {'fields': ['code', 'voucher', 'voucher_locality',
                                                     'voucher_code']}
                  ),

                 ('Specimen Information', {'fields': ['orden', 'superfamily', 'family',
                                                      'subfamily', 'tribe', 'subtribe',
                                                      'genus', 'species', 'subspecies',
                                                      'hostorg', 'author', 'type_species',
                                                      ],
                                           'classes': ['collapse']}),

                 ('Collection Information', {'fields': ['country', 'specific_locality',
                                                        'latitude', 'longitude',
                                                        'max_altitude', 'min_altitude',
                                                        'collector', 'code_bold',
                                                        'date_collection',
                                                        'date_collection_end',
                                                        'determined_by',
                                                        'sex', 'extractor', 'extraction',
                                                        'extraction_tube', 'notes',
                                                        'published_in', 'date_extraction',
                                                        'edits', 'latest_editor',
                                                        ],
                                             'classes': ['collapse']}),
                 ]

    def batch_changes(self, request, queryset):
        # Check that the user has change permission for the actual model
        if not self.has_change_permission(request):
            raise PermissionDenied
        else:
            selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
            new_request = HttpRequest()
            new_request.method = 'GET'
            return change_selected(new_request, ",".join(selected))

    batch_changes.short_description = "Change selected in batch"
    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput}
    }

    if settings.PHOTOS_REPOSITORY == 'flickr':
        inlines = [FlickImageInLine, ]
    else:
        inlines = [ImageInLine, ]

    resource_class = BatchImportVouchersResource


class SequencesAdmin(ImportExportModelAdmin):
    # import_template_name = 'admin/public_interface/sequences/batch_import.html'
    # TODO let users know that code and genecode keywords act as AND boolean search
    search_fields = ['code__code', 'gene__gene_code', 'accession']
    list_display = ['code', 'gene', 'genbank', 'accession', 'lab_person',
                    'notes', 'time_edited', 'time_created']
    fields = ['code', 'gene', 'sequences', 'genbank', 'accession',
              'lab_person', 'notes']
    form = SequencesAdminForm
    resource_class = BatchImportSequencesResource


class TaxonSetsAdmin(admin.ModelAdmin):
    list_display = ['taxonset_name', 'taxonset_creator', 'taxonset_description']


class GeneSetsAdmin(admin.ModelAdmin):
    list_display = ['geneset_name', 'geneset_creator', 'geneset_description']


class GenesAdmin(ImportExportModelAdmin):
    list_display = ['gene_code', 'description', 'genetic_code', 'length',
                    'reading_frame', 'aligned', 'intron', 'prot_code',
                    'gene_type', 'notes']
    resource_classes = [BatchImportGenesResource]


# Register your models here.
admin.site.register(Sequences, SequencesAdmin)
admin.site.register(GeneSets, GeneSetsAdmin)
admin.site.register(Genes, GenesAdmin)
admin.site.register(TaxonSets, TaxonSetsAdmin)
admin.site.register(Vouchers, VouchersAdmin)
