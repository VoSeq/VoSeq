from django import forms

from core.forms import BaseDatasetForm


class CreateDatasetForm(BaseDatasetForm):
    file_format = forms.ChoiceField(
        label='Choose file format',
        choices=[
            ('TNT', 'TNT format'),
            ('NEXUS', 'NEXUS format'),
            ('PHYLIP', 'PHYLIP format'),
            ('MEGA', 'MEGA format'),
            ('FASTA', 'Unaligned FASTA format'),
            ('Bankit', 'Bankit format'),
        ],
        widget=forms.RadioSelect(),
        required=True,
        initial='FASTA',
    )

    outgroup = forms.CharField(
        label='Outgroup (code, for NEXUS and TNT)',
        help_text='Voucher code for using that specimen\'s sequence as '
                  'outgroup in NEXUS and TNT datasets.',
        required=False,
    )

    positions = forms.MultipleChoiceField(
        label='Codon Positions',
        help_text='Codon positions to keep and write into datasets',
        choices=[
            ('ALL', 'all'),
            ('1st', '1st'),
            ('2nd', '2nd'),
            ('3rd', '3rd'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        initial=['ALL'],
        required=True,
    )

    partition_by_positions = forms.ChoiceField(
        label='Partition by positions',
        choices=[
            ('by gene', 'by gene'),
            ('by codon position', 'by codon position'),
            ('1st-2nd, 3rd', '1st-2nd, 3rd'),
        ],
        widget=forms.RadioSelect(),
        initial='by gene',
        required=True,
    )

    translations = forms.BooleanField(
        label='Degen(erated)',
        widget=forms.CheckboxInput(),
        required=False,
    )

    aminoacids = forms.BooleanField(
        label='Amino acids',
        widget=forms.CheckboxInput(),
        required=False,
    )

    degen_translations = forms.ChoiceField(
        label='Degenerated translations)',
        choices=[
            ('normal', 'normal'),
            ('S', 'S'),
            ('Z', 'Z'),
            ('SZ', 'SZ'),
        ],
        widget=forms.RadioSelect(),
        initial='normal',
        required=True,
    )

    special = forms.BooleanField(
        label='Special',
        widget=forms.CheckboxInput(),
        required=False,
    )

    taxon_names = forms.MultipleChoiceField(
        label='What info do you want in the taxon names?',
        choices=[
            ('CODE', 'Code'),
            ('ORDEN', 'Order'),
            ('SUPERFAMILY', 'Superfamily'),
            ('FAMILY', 'Family'),
            ('SUBFAMILY', 'Subfamily'),
            ('TRIBE', 'Tribe'),
            ('SUBTRIBE', 'Subtribe'),
            ('GENUS', 'Genus'),
            ('SPECIES', 'Species'),
            ('SUBSPECIES', 'Subspecies'),
            ('AUTHOR', 'Author'),
            ('HOSTORG', 'Host org.'),
            ('GENECODE', 'Gene code'),
            ('COUNTRY', 'Country'),
            ('SPECIFIC_LOCALITY', 'Specific Locality'),
        ],
        widget=forms.CheckboxSelectMultiple(),
        initial=['CODE', 'GENUS', 'SPECIES'],
        required=False,
        help_text='If taxon_names is None, use standart code_genus_species',
    )

    number_genes = forms.IntegerField(
        label='Minimum number of genes',
        required=False,
    )

    introns = forms.ChoiceField(
        choices=[
            ('YES', 'yes'),
            ('NO', 'no'),
        ],
        widget=forms.RadioSelect(),
        initial='YES',
        required=True,
        help_text='Ignore introns?',
    )
