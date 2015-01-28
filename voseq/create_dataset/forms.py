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

    aminoacids = forms.ChoiceField(
        label='Amino acids',
        widget=forms.CheckboxInput(),
    )

    degen_translations = forms.ChoiceField(
        label='Degenerated translations)',
        widget=forms.RadioSelect(),
        choices=[
            ('NORMAL', 'normal'),
            ('S', 'S'),
            ('Z', 'Z'),
            ('SZ', 'SZ'),
        ]
    )

    special = forms.ChoiceField(
        label='Special',
        widget=forms.CheckboxInput(),
    )

    taxon_names = forms.ChoiceField(
        label='What info do you want in the taxon names?',
        choices=[
            ('CODE', 'Code'),
            ('ORDER', 'Order'),
            ('FAMILY', 'Family'),
            ('SUBFAMILY', 'Subfamily'),
            ('TRIBE', 'Tribe'),
            ('SUBTRIBE', 'Subtribe'),
            ('GENUS', 'Genus'),
            ('SPECIES', 'Species'),
            ('SUBSPECIES', 'Subspecies'),
            ('AUCTOR', 'Auctor'),
            ('HOSTORG', 'Host org.'),
            ('GENECODE', 'Gene code'),
        ],
        widget=forms.CheckboxSelectMultiple(),
    )

    exclude = forms.ChoiceField(
        help_text='If dataset is for single gene, exclude taxa missing this gene? '
                  'Otherwise include taxon with ? as sequences.',
        choices=[
            ('YES', 'yes'),
            ('NO', 'no'),
        ],
        widget=forms.RadioSelect(),
    )

    number_genes = forms.IntegerField(
        label='Minimum number of genes',
    )

    introns = forms.ChoiceField(
        choices=[
            ('YES', 'yes'),
            ('NO', 'no'),
        ],
        widget=forms.RadioSelect(),
    )
