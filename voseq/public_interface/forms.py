import datetime
from functools import partial
from typing import Dict, Tuple

from django import forms
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from Bio.Alphabet import IUPAC

from public_interface.models import Genes, Vouchers, Sequences


DateInput = partial(forms.DateInput, {'class': 'datepicker form-control',
                                      'placeholder': 'Type or pick a date'})


class SequencesAdminForm(forms.ModelForm):
    def clean_sequences(self) -> str:
        valid_letters = set(IUPAC.ambiguous_dna.letters.upper() + 'N?-')
        sequence = str(self.cleaned_data['sequences'])
        for nucleotide in sequence:
            if nucleotide == ' ':
                self.add_error('sequences', "White spaces are not valid. "
                                            "Cannot save this sequence")
            elif not valid_letters.issuperset(nucleotide.upper()):
                self.add_error('sequences',
                               "The character {} is not valid. "
                               "Cannot save this sequence".format(nucleotide))
        return sequence


class AdvancedSearchForm(ModelSearchForm):
    NULL = 'Select'
    MALE = 'male'
    FEMALE = 'female'
    LARVA = 'larva'
    WORKER = 'worker'
    QUEEN = 'queen'
    UNKNOWN = 'unknown'
    SEX_CHOICES = (
        (NULL, 'Select'),
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
        (UNKNOWN, 'unknown'),
    )

    NULL = 'Select'
    DONT_KNOW = 'unknown'
    YES = 'yes'
    NO = 'not'
    TYPE_SPECIES_CHOICES = (
        (NULL, 'Select'),
        (DONT_KNOW, 'unknown'),
        (YES, 'yes'),
        (NO, 'not'),
    )

    NULL = 'Select'
    SPREAD = 'spread'
    ENVELOPE = 'in envelope'
    PHOTO = 'only photo'
    NONE = 'no voucher'
    DESTROYED = 'destroyed'
    LOST = 'lost'
    VOUCHER_CHOICES = (
        (NULL, 'Select'),
        (SPREAD, 'spread'),
        (ENVELOPE, 'in envelope'),
        (PHOTO, 'only photo'),
        (NONE, 'no voucher'),
        (DESTROYED, 'destroyed'),
        (LOST, 'lost'),
        (UNKNOWN, 'unknown'),
    )
    code = forms.CharField(label="Code in voseq", max_length=100, required=False)
    orden = forms.CharField(label="Order", max_length=100, required=False)
    superfamily = forms.CharField(label="Superfamily", max_length=100, required=False)
    family = forms.CharField(label="Family", max_length=100, required=False)
    subfamily = forms.CharField(label="Subfamily", max_length=100, required=False)
    tribe = forms.CharField(label="Tribe", max_length=100, required=False)
    subtribe = forms.CharField(label="Subtribe", max_length=100, required=False)
    genus = forms.CharField(label="Genus", max_length=100, required=False)
    species = forms.CharField(label="Species", max_length=100, required=False)
    subspecies = forms.CharField(label="Subspecies", max_length=100, required=False)
    country = forms.CharField(label="Country", max_length=100, required=False)
    specific_locality = forms.CharField(
        label="Specific Locality",
        max_length=250,
        required=False)
    type_species = forms.ChoiceField(
        label="Type species",
        choices=TYPE_SPECIES_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False)
    latitude = forms.FloatField(label="Latitude", required=False)
    longitude = forms.FloatField(label="Longitude", required=False)
    max_altitude = forms.IntegerField(label="Maximum altitude", required=False)
    min_altitude = forms.IntegerField(label="Minimum altitude", required=False)
    collector = forms.CharField(label="Collector", max_length=100, required=False)
    date_collection = forms.DateField(
        label="Date of collection start",
        required=False,
        widget=DateInput(),
        error_messages={'invalid': 'Enter valid date: YYYY-mm-dd'},
    )
    date_collection_end = forms.DateField(
        label="Date of collection end",
        required=False,
        widget=DateInput(),
        error_messages={'invalid': 'Enter valid date: YYYY-mm-dd'},
    )
    extraction = forms.CharField(
        label="Extraction",
        max_length=50,
        help_text="Number of extraction event.",
        required=False)
    extraction_tube = forms.CharField(
        label="Extraction tube",
        max_length=50,
        help_text="Tube containing DNA extract.",
        required=False)
    date_extraction = forms.DateField(
        label="Date of extraction",
        required=False,
        widget=DateInput(),
        error_messages={'invalid': 'Enter valid date: YYYY-mm-dd'})
    extractor = forms.CharField(label="Extractor", max_length=100, required=False)
    voucher_locality = forms.CharField(
        label="Voucher locality",
        max_length=200,
        required=False)
    published_in = forms.CharField(label="Published in", required=False)
    notes = forms.CharField(label="Notes", required=False)
    latest_editor = forms.CharField(label="Latest editor", required=False)
    hostorg = forms.CharField(
        label="Host organism",
        max_length=200,
        help_text="Hostplant or other host.",
        required=False)
    sex = forms.ChoiceField(label="Sex", choices=SEX_CHOICES, required=False,
                            widget=forms.Select(attrs={'class': 'form-control'}))
    voucher = forms.ChoiceField(
        label="Voucher",
        choices=VOUCHER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}))
    voucher_code = forms.CharField(
        label="Alternative voucher code",
        max_length=100,
        help_text="Original code of voucher specimen.",
        required=False)
    code_bold = forms.CharField(
        label="Code in BOLD database",
        max_length=100,
        help_text="Optional code for specimens kept in the BOLD database.",
        required=False)
    determined_by = forms.CharField(
        label="Determined by",
        max_length=100,
        help_text="Person that identified the taxon for this specimen.",
        required=False)
    author = forms.CharField(
        label="Author",
        max_length=100,
        help_text="Person that described this taxon.",
        required=False)

    # Sequences model
    YES = 'y'
    NO = 'n'
    GENBANK_CHOICES = (
        (YES, 'Yes'),
        (NO, 'No'),
    )
    gene_code = forms.ModelChoiceField(
        Genes.objects.all().order_by('gene_code'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label='Select',
    )
    genbank = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=GENBANK_CHOICES,
        required=False)
    accession = forms.CharField(max_length=100, required=False)
    lab_person = forms.CharField(max_length=100, required=False)

    def no_query_found(self):
        sqs = SearchQuerySet.none
        return sqs

    def search(self):
        keywords, sequence_keywords = self.clean_search_keywords()
        sqs = ''
        if keywords and not sequence_keywords:
            sqs = Vouchers.objects.filter(**keywords).distinct("code")
        elif sequence_keywords and not keywords:
            sqs = Sequences.objects.filter(**sequence_keywords).distinct("code")
        elif sequence_keywords and keywords:
            sqs = Vouchers.objects.filter(**keywords).distinct("code")
            if sqs:
                voucher_list = sqs
                sqs = Sequences.objects.filter(**sequence_keywords).filter(
                    code__in=voucher_list).distinct("code")
            else:
                sqs = self.no_query_found()

        if not sqs:
            sqs = self.no_query_found()
        return sqs

    def clean_search_keywords(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        keywords = {}
        sequence_keywords = {}
        for key, value in self.cleaned_data.items():
            if value in ['', None, 'Select', 'models'] or key == "models":
                continue

            if key in ['date_collection', 'date_collection_end', 'date_extraction']:
                value = datetime.date.strftime(value, "%Y-%m-%d")
            if key in ['lab_person', 'accession']:
                new_key = "{}__icontains".format(key)
                sequence_keywords[new_key] = value
            if key == 'gene_code':
                new_key = "{}__icontains".format(key)
                sequence_keywords[new_key] = value.gene_code
            if key == 'genbank' and value == 'y':
                sequence_keywords[key] = True
            elif key == 'genbank':
                sequence_keywords[key] = False
            if key not in ['lab_person', 'accession', 'genbank', 'gene_code']:
                new_key = "{}__icontains".format(key)
                keywords[new_key] = value

        return keywords, sequence_keywords


# The following form is for the admin site batch_changes action
# It would be nice not to repeat the lines from the previous
# model, but...
class BatchChangesForm(forms.Form):
    NULL = None
    MALE = 'male'
    FEMALE = 'female'
    LARVA = 'larva'
    WORKER = 'worker'
    QUEEN = 'queen'
    SEX_CHOICES = (
        (NULL, 'Select'),
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
    )

    NULL = None
    DONT_KNOW = 'unknown'
    YES = 'yes'
    NO = 'not'
    TYPE_SPECIES_CHOICES = (
        (NULL, 'Select'),
        (DONT_KNOW, 'unknown'),
        (YES, 'yes'),
        (NO, 'not'),
    )
    NULL = None
    SPREAD = 'spread'
    ENVELOPE = 'in envelope'
    PHOTO = 'only photo'
    NONE = 'no voucher'
    DESTROYED = 'destroyed'
    LOST = 'lost'
    VOUCHER_CHOICES = (
        (NULL, 'Select'),
        (SPREAD, 'spread'),
        (ENVELOPE, 'in envelope'),
        (PHOTO, 'only photo'),
        (NONE, 'no voucher'),
        (DESTROYED, 'destroyed'),
        (LOST, 'lost'),
    )
    code = forms.CharField(label="Code in voseq", max_length=100, required=False)
    orden = forms.CharField(label="Order", max_length=100, required=False)
    superfamily = forms.CharField(label="Superfamily", max_length=100, required=False)
    family = forms.CharField(label="Family", max_length=100, required=False)
    subfamily = forms.CharField(label="Subfamily", max_length=100, required=False)
    tribe = forms.CharField(label="Tribe", max_length=100, required=False)
    subtribe = forms.CharField(label="Subtribe", max_length=100, required=False)
    genus = forms.CharField(label="Genus", max_length=100, required=False)
    species = forms.CharField(label="Species", max_length=100, required=False)
    subspecies = forms.CharField(label="Subspecies", max_length=100, required=False)
    country = forms.CharField(label="Country", max_length=100, required=False)
    specific_locality = forms.CharField(
        label="Specific Locality",
        max_length=250,
        required=False)
    type_species = forms.ChoiceField(
        label="Type species",
        choices=TYPE_SPECIES_CHOICES,
        widget=forms.Select,
        required=False)
    latitude = forms.FloatField(label="Latitude", required=False)
    longitude = forms.FloatField(label="Longitude", required=False)
    max_altitude = forms.IntegerField(label="Maximum altitude", required=False)
    min_altitude = forms.IntegerField(label="Minimum altitude", required=False)
    collector = forms.CharField(label="Collector", max_length=100, required=False)
    date_collection = forms.DateField(label="Date of collection start", required=False)
    date_collection_end = forms.DateField(label="Date of collection end", required=False)
    extraction = forms.CharField(
        label="Extraction",
        max_length=50,
        help_text="Number of extraction event.",
        required=False)
    extraction_tube = forms.CharField(
        label="Extraction tube",
        max_length=50,
        help_text="Tube containing DNA extract.",
        required=False)
    date_extraction = forms.DateField(label="Date extraction", required=False)
    extractor = forms.CharField(label="Extractor", max_length=100, required=False)
    voucher_locality = forms.CharField(
        label="Voucher locality",
        max_length=200,
        required=False)
    published_in = forms.CharField(label="Published in", required=False)
    notes = forms.CharField(label="Notes", required=False)
    latest_editor = forms.CharField(label="Latest editor", required=False)
    hostorg = forms.CharField(
        label="Host organism",
        max_length=200,
        help_text="Hostplant or other host.",
        required=False)
    sex = forms.ChoiceField(
        label="Sex",
        choices=SEX_CHOICES,
        required=False)
    voucher = forms.ChoiceField(
        label="Voucher",
        choices=VOUCHER_CHOICES,
        required=False)
    voucher_code = forms.CharField(
        label="Alternative voucher code",
        max_length=100,
        help_text="Original code of voucher specimen.",
        required=False)
    code_bold = forms.CharField(
        label="Code in BOLD database",
        max_length=100,
        help_text="Optional code for specimens kept in the BOLD database.",
        required=False)
    determined_by = forms.CharField(
        label="Determined by",
        max_length=100,
        help_text="Person that identified the taxon for this specimen.",
        required=False)
    author = forms.CharField(
        label="Author",
        max_length=100,
        help_text="Person that described this taxon.",
        required=False)
