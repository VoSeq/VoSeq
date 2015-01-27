from django import forms

from core.forms import BaseDatasetForm


class CreateDatasetForm(BaseDatasetForm):
    file_format = forms.ChoiceField(
        label='Choose file format',
        choices=[
            ('TNT', 'TNT format'),
            ('NEXUS', 'NEXUS format'),
            ('PHY', 'PHYLIP format'),
            ('FASTA', 'Unaligned FASTA format'),
        ],
        widget=forms.RadioSelect(),
    )

    outgroup = forms.CharField(
        label='Outgroup (code, for NEXUS and TNT)',
        help_text='Voucher code for using that specimen\'s sequence as '
                  'outgroup in NEXUS and TNT datasets.',
    )

    positions = forms.ChoiceField(
        label='Positions',
        help_text='codon positions',
        choices=[
            ('ALL', 'all'),
            ('1st', '1st'),
            ('2nd', '2nd'),
            ('3rd', '3rd'),
        ],
        widget=forms.CheckboxSelectMultiple(),
    )

    partition_by_positions = forms.ChoiceField(
        label='Partition by positions',
        choices=[
            ('ONE', 'as one'),
            ('EACH', 'each'),
            ('1st-3rd', '1st-2nd, 3rd'),
        ],
        widget=forms.CheckboxSelectMultiple(),
    )

    translations = forms.ChoiceField(
        label='Degen(erated)',
        widget=forms.CheckboxInput(),
    )
