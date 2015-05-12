from django import forms
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet

from public_interface.models import Genes


class AdvancedSearchForm(ModelSearchForm):
    NULL = 'Select'
    MALE = 'm'
    FEMALE = 'f'
    LARVA = 'l'
    WORKER = 'w'
    QUEEN = 'q'
    SEX_CHOICES = (
        (NULL, 'Select'),
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
    )

    NULL = 'Select'
    DONT_KNOW = 'd'
    YES = 'y'
    NO = 'n'
    TYPE_SPECIES_CHOICES = (
        (NULL, 'Select'),
        (DONT_KNOW, 'don\'t know'),
        (YES, 'yes'),
        (NO, 'no'),
    )

    NULL = 'Select'
    SPREAD = 's'
    ENVELOPE = 'e'
    PHOTO = 'p'
    NONE = 'n'
    DESTROYED = 'd'
    LOST = 'l'
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
    specificLocality = forms.CharField(label="Specific Locality", max_length=250, required=False)
    typeSpecies = forms.ChoiceField(label="Type species", choices=TYPE_SPECIES_CHOICES, widget=forms.Select, required=False)
    latitude = forms.FloatField(label="Latitude", required=False)
    longitude = forms.FloatField(label="Longitude", required=False)
    max_altitude = forms.IntegerField(label="Maximum altitude", required=False)
    min_altitude = forms.IntegerField(label="Minimum altitude", required=False)
    collector = forms.CharField(label="Collector", max_length=100, required=False)
    dateCollection = forms.DateField(label="Date of collection", required=False)
    extraction = forms.CharField(label="Extraction", max_length=50, help_text="Number of extraction event.", required=False)
    extractionTube = forms.CharField(label="Extraction tube", max_length=50, help_text="Tube containing DNA extract.", required=False)
    dateExtraction = forms.DateField(label="Date extraction", required=False)
    extractor = forms.CharField(label="Extractor", max_length=100, required=False)
    voucherLocality = forms.CharField(label="Voucher locality", max_length=200, required=False)
    publishedIn = forms.CharField(label="Published in", required=False)
    notes = forms.CharField(label="Notes", required=False)
    latesteditor = forms.CharField(label="Latest editor", required=False)
    hostorg = forms.CharField(label="Host organism", max_length=200, help_text="Hostplant or other host.", required=False)
    sex = forms.ChoiceField(label="Sex", choices=SEX_CHOICES, required=False)
    voucher = forms.ChoiceField(label="Voucher", choices=VOUCHER_CHOICES, required=False)
    voucherCode = forms.CharField(label="Alternative voucher code", max_length=100, help_text="Original code of voucher specimen.", required=False)
    code_bold = forms.CharField(label="Code in BOLD database", max_length=100, help_text="Optional code for specimens kept in the BOLD database.",
                                required=False)
    determinedBy = forms.CharField(label="Determined by", max_length=100, help_text="Person that identified the taxon for this specimen.",
                                   required=False)
    author = forms.CharField(label="Author", max_length=100, help_text="Person that described this taxon.", required=False)

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
        widget=forms.Select(),
        empty_label='Select',
    )
    genbank = forms.ChoiceField(widget=forms.RadioSelect, choices=GENBANK_CHOICES, required=False)
    accession = forms.CharField(max_length=100, required=False)
    labPerson = forms.CharField(max_length=100, required=False)

    def no_query_found(self):
        sqs = SearchQuerySet.none
        return sqs

    def search(self):
        keywords = {}
        sequence_keywords = {}
        for k, v in self.cleaned_data.items():
            print(k, v)
            if v != '' and v is not None:
                # remove after adding this to index
                if k == 'sex' or k == 'typeSpecies' or k == 'voucher' or k == 'models':
                    continue
                if k == 'labPerson' or k == 'accession':
                    sequence_keywords[k] = v
                if k == 'genbank':
                    if v == 'y':
                        sequence_keywords[k] = 'true'
                    else:
                        sequence_keywords[k] = 'false'
                if k not in ['labPerson', 'accession', 'genbank']:
                    keywords[k] = v
        print(keywords)

        # Check if we got any input value to search from
        sqs = ''
        if bool(sequence_keywords) is True:
            sqs = SearchQuerySet().using('advanced_search').filter(**sequence_keywords).facet('code')
            sqs = filter_results_from_sequence_table(sqs)
        if bool(keywords) is True:
            if sqs != '':
                sqs = sqs.filter(**keywords)
            else:
                sqs = SearchQuerySet().using('vouchers').filter(**keywords)

        if len(sqs) > 0:
            return sqs
        else:
            self.no_query_found()


def filter_results_from_sequence_table(sqs):
    """Need to avoid returning duplicated voucher results.
    """
    facet_counts = sqs.facet_counts()
    voucher_codes_count = facet_counts['fields']['code']
    if len(voucher_codes_count) > 0:
        voucher_codes = [item[0] for item in voucher_codes_count]
        filtered_sqs = SearchQuerySet().using('vouchers').filter(code__in=voucher_codes)
        return filtered_sqs
    else:
        return sqs


# The following form is for the admin site bacth_changes action
# It would be nice not to repeat the lines from the previous
# model, but...
class BatchChangesForm(forms.Form):
    '''
    class Meta:
        model = Vouchers
        fields = ['orden', 'superfamily', 'family', 'subfamily', 'tribe', 'subtribe',
                  'genus', 'species', 'subspecies', 'typeSpecies', 'sex', 'author',
                  'determinedBy', 'publishedIn', 'country', 'specificLocality', 'latitude',
                  'longitude', 'max_altitude', 'min_altitude', 'dateCollection', 'collector',
                  'hostorg', 'dateExtraction', 'extractor', 'extraction', 'extractionTube',
                  'voucher', 'voucherLocality', 'latesteditor', 'edits', 'notes']
    '''

    NULL = None
    MALE = 'm'
    FEMALE = 'f'
    LARVA = 'l'
    WORKER = 'w'
    QUEEN = 'q'
    SEX_CHOICES = (
        (NULL, 'Select'),
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
    )

    NULL = None
    DONT_KNOW = 'd'
    YES = 'y'
    NO = 'n'
    TYPE_SPECIES_CHOICES = (
        (NULL, 'Select'),
        (DONT_KNOW, 'don\'t know'),
        (YES, 'yes'),
        (NO, 'no'),
    )
    NULL = None
    SPREAD = 's'
    ENVELOPE = 'e'
    PHOTO = 'p'
    NONE = 'n'
    DESTROYED = 'd'
    LOST = 'l'
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
    specificLocality = forms.CharField(label="Specific Locality", max_length=250, required=False)
    typeSpecies = forms.ChoiceField(label="Type species", choices=TYPE_SPECIES_CHOICES, widget=forms.Select, required=False)
    latitude = forms.FloatField(label="Latitude", required=False)
    longitude = forms.FloatField(label="Longitude", required=False)
    max_altitude = forms.IntegerField(label="Maximum altitude", required=False)
    min_altitude = forms.IntegerField(label="Minimum altitude", required=False)
    collector = forms.CharField(label="Collector", max_length=100, required=False)
    dateCollection = forms.DateField(label="Date of collection", required=False)
    extraction = forms.CharField(label="Extraction", max_length=50, help_text="Number of extraction event.", required=False)
    extractionTube = forms.CharField(label="Extraction tube", max_length=50, help_text="Tube containing DNA extract.", required=False)
    dateExtraction = forms.DateField(label="Date extraction", required=False)
    extractor = forms.CharField(label="Extractor", max_length=100, required=False)
    voucherLocality = forms.CharField(label="Voucher locality", max_length=200, required=False)
    publishedIn = forms.CharField(label="Published in", required=False)
    notes = forms.CharField(label="Notes", required=False)
    latesteditor = forms.CharField(label="Latest editor", required=False)
    hostorg = forms.CharField(label="Host organism", max_length=200, help_text="Hostplant or other host.", required=False)
    sex = forms.ChoiceField(label="Sex", choices=SEX_CHOICES, required=False)
    voucher = forms.ChoiceField(label="Voucher", choices=VOUCHER_CHOICES, required=False)
    voucherCode = forms.CharField(label="Alternative voucher code", max_length=100, help_text="Original code of voucher specimen.", required=False)
    code_bold = forms.CharField(label="Code in BOLD database", max_length=100, help_text="Optional code for specimens kept in the BOLD database.",
                                required=False)
    determinedBy = forms.CharField(label="Determined by", max_length=100, help_text="Person that identified the taxon for this specimen.",
                                   required=False)
    author = forms.CharField(label="Author", max_length=100, help_text="Person that described this taxon.", required=False)
