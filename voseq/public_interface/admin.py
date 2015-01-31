from django.contrib import admin

from public_interface.models import Vouchers

# Customize what and the way you show it
# class VouchersAdmin(admin.ModelAdmin):

class VouchersAdmin(admin.ModelAdmin):
    list_display = ['code', 'genus', 'species', 'sex', 'voucher', 'country', 'collector']
    ordering = ['code']
    #actions = []

    fieldsets = [('Voucher Information', {'fields': ['code', 'voucher', 'voucherLocality',
                                                     'voucherCode','code_bold']}
                  ),
                 
                 ('Specimen Information', {'fields': ['orden', 'superfamily',
                                                      'family', 'subfamily',
                                                      'tribe', 'subtribe',
                                                      'genus', 'species',
                                                      'subspecies', 'sex',
                                                      'typeSpecies'],
                  'classes': ['collapse']}
                  ),
                 
                 ('Collection Information', {'fields': ['country','specificLocality',
                                                        'latitude','longitude',
                                                        'max_altitude', 'min_altitude',
                                                        'collector', 'dateCollection',
                                                        'hostorg', 'extraction',
                                                        'extractionTube', 'extractor',
                                                        'dateExtraction', 'determinedBy',
                                                        'author', 'publishedIn', 'notes',
                                                        'edits', 'latesteditor'],
                  'classes': ['collapse']}
                  ),
                 
                 (None, {'fields': ['timestamp']}),
                 ]


# Register your models here.
admin.site.register(Vouchers, VouchersAdmin)
