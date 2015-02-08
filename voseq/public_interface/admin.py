from django.contrib import admin

from public_interface.models import Vouchers
from django.http import HttpRequest, HttpResponseRedirect
from public_interface.views import change_selected
from django.core.exceptions import PermissionDenied


# Customize what and the way you show it
# class VouchersAdmin(admin.ModelAdmin):


class VouchersAdmin(admin.ModelAdmin):
    list_display = ['code', 'genus', 'species', 'sex', 'voucher', 'country', 'collector']
    ordering = ['code']
    list_filter = ['voucher']
    search_fields = ['=genus', '=species']
    
    #list_editable = ['genus', 'species', 'sex', 'voucher', 'country', 'collector']
    
    actions = ['batch_changes']

    fieldsets = [('Voucher Information', {'fields': ['code', 'voucher', 'voucherLocality',
                                                     'voucherCode','code_bold']}
                  ),
                 
                 ('Specimen Information', {'fields': [('orden', 'superfamily',
                                                      'family'), ('subfamily',
                                                      'tribe', 'subtribe'),
                                                      ('genus', 'species',
                                                      'subspecies'), ('sex', 'typeSpecies'),
                                                      ('author', 'determinedBy'), 'publishedIn'],
                  'classes': ['collapse']}
                  ),
                 
                 ('Collection Information', {'fields': [('country','specificLocality'),
                                                        ('latitude','longitude'),
                                                        ('max_altitude', 'min_altitude'),
                                                        'dateCollection', ('collector',
                                                        'hostorg'), 'dateExtraction',
                                                        ('extractor','extraction',
                                                         'extractionTube'), 'notes',
                                                        'edits', 'latesteditor'],
                  'classes': ['collapse']}
                  ),
                 
                 (None, {'fields': ['timestamp']}),
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
                #return HttpResponseRedirect("/admin/public_interface/vouchers/batch_changes/ids=%s" % ",".join(selected))

# Register your models here.
admin.site.register(Vouchers, VouchersAdmin)
