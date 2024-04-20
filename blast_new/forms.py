from django import forms

from public_interface.models import Genes


class BLASTNewForm(forms.Form):
    name = forms.CharField(
        label='Name',
        required=True,
        max_length=100,
    )
    sequence = forms.CharField(
        label='Sequence',
        required=True,
        widget=forms.Textarea,
    )

    gene_codes = forms.ModelMultipleChoiceField(
        Genes.objects.all(),
        label='Genes',
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        to_field_name='gene_code',
    )

    def clean_sequence(self):
        data = self.cleaned_data['sequence']
        invalid_characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for i in invalid_characters:
            if i in data:
                raise forms.ValidationError(f'Sequence contains invalid characters: {i}')

        if data.strip() == '':
            raise forms.ValidationError('Sequence is empty')

        return data
