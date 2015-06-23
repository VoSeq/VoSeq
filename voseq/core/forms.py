from django import forms

from public_interface.models import Genes
from public_interface.models import GeneSets
from public_interface.models import TaxonSets


class BaseDatasetForm(forms.Form):
    """Base class for datasets.

    * Handles list of voucher codes including those from taxonsets.
    * Handles list of gene codes including those from genesets.

    Other dataset classes should inherit from this one.

    """
    taxonset = forms.ModelChoiceField(
        TaxonSets.objects.all(),
        label='Choose taxonset',
        required=False,
        empty_label='Choose taxonset',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    geneset = forms.ModelChoiceField(
        GeneSets.objects.all(),
        label='Choose geneset',
        required=False,
        empty_label='Choose geneset',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    gene_codes = forms.ModelMultipleChoiceField(
        Genes.objects.all().order_by('gene_code'),
        label='Check to select your alignment/gene',
        required=False,
        widget=forms.CheckboxSelectMultiple(),
    )
    voucher_codes = forms.CharField(
        widget=forms.Textarea,
        label='... and/or a list of voucher codes',
        required=False,
    )

    def clean(self):
        """Overwriting validator method of class form.

        Drops vouchers if their codes have been flagged by users with two
            consecutive dashes ``--``.

        Returns:
            Sets of voucher and genes codes.

        """
        cleaned_data = super(BaseDatasetForm, self).clean()
        taxonset = cleaned_data.get("taxonset")
        voucher_codes = cleaned_data.get("voucher_codes")

        geneset = cleaned_data.get("geneset")
        gene_codes = cleaned_data.get("gene_codes")

        if taxonset is None and voucher_codes.strip() == '':
            raise forms.ValidationError("You need to enter at least some "
                                        "voucher codes or select a taxonset.")

        if geneset is None and len(gene_codes) < 1:
            raise forms.ValidationError("You need to enter at least some "
                                        "gene codes or select a geneset.")
