from django import forms

from core.forms import BaseDatasetForm


class VoucherTableForm(BaseDatasetForm):
    voucher_info = forms.MultipleChoiceField(
        label='Voucher info:',
        choices=[
            ('code', 'Code'),
            ('orden', 'Order'),
            ('superfamily', 'Superfamily'),
            ('family', 'Family'),
            ('subfamily', 'Subfamily'),
            ('tribe', 'Tribe'),
            ('subtribe', 'Subtribe'),
            ('genus', 'Genus'),
            ('species', 'Species'),
            ('subspecies', 'Subspecies'),
            ('author', 'Author'),
            ('hostorg', 'Host org.'),
            ('type_species', 'Type species'),
            ('voucher_code', 'Alternative voucher code'),
            ('notes', 'Notes'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        initial=['code', 'genus', 'species'],
        required=False,
        help_text='If taxon_names is None, use standard code_genus_species',
    )
    collector_info = forms.MultipleChoiceField(
        label='Locality and collector info:',
        choices=[
            ('country', 'Country'),
            ('specific_locality', 'Locality'),
            ('collector', 'Collector'),
            ('date_collection', 'Coll. date'),
            ('determined_by', 'Determined by'),
            ('min_altitude', 'Minimum Altitude'),
            ('max_altitude', 'Maximum Altitude'),
            ('latitude', 'Latitude'),
            ('longitude', 'Longitude'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    gene_info = forms.ChoiceField(
        label='Choose what gene info to display:',
        choices=[
            ('NUMBER OF BASES', 'Number of bases'),
            ('ACCESSION NUMBER', 'Accession number'),
            ('EXIST OR EMPTY', 'X/- (exists/empty)'),
        ],
        widget=forms.RadioSelect(),
        required=False,
    )
    field_delimitor = forms.ChoiceField(
        label='Choose your field delimiter:',
        choices=[
            ('COMMA', 'comma'),
            ('TAB', 'tab'),
        ],
        widget=forms.RadioSelect(),
        required=False,
    )
