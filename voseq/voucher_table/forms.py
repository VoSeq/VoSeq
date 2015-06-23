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
        ],
        widget=forms.CheckboxSelectMultiple(),
        initial=['code', 'genus', 'species'],
        required=False,
        help_text='If taxon_names is None, use standart code_genus_species',
    )
    collector_info = forms.MultipleChoiceField(
        label='Locality and collector info:',
        choices=[
            ('country', 'Country'),
            ('specificLocality', 'Locality'),
            ('collector', 'Collector'),
            ('dateCollection', 'Coll. date'),
            ('determinedBy', 'Determined by'),
            ('altitude', 'Altitude'),
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
        label='Choose your field delimitor:',
        choices=[
            ('COMMA', 'comma'),
            ('TAB', 'tab'),
        ],
        widget=forms.RadioSelect(),
        required=False,
    )
