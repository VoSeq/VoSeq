import datetime

from haystack import indexes

from public_interface.models import Vouchers
from public_interface.models import Sequences


class SimpleSearchIndex(indexes.SearchIndex, indexes.Indexable):
    """We have only taxonomical fields for this search.
    """
    text = indexes.EdgeNgramField(document=True, use_template=True)
    code = indexes.EdgeNgramField(model_attr='code')
    orden = indexes.EdgeNgramField(model_attr='orden', null=True)
    superfamily = indexes.EdgeNgramField(model_attr='superfamily', null=True)
    family = indexes.EdgeNgramField(model_attr='family', null=True)
    subfamily = indexes.EdgeNgramField(model_attr='subfamily', null=True)
    tribe = indexes.EdgeNgramField(model_attr='tribe', null=True)
    subtribe = indexes.EdgeNgramField(model_attr='subtribe', null=True)
    genus = indexes.EdgeNgramField(model_attr='genus', null=True)
    species = indexes.EdgeNgramField(model_attr='species', null=True)
    subspecies = indexes.EdgeNgramField(model_attr='subspecies', null=True)
    hostorg = indexes.EdgeNgramField(model_attr='hostorg', null=True)

    def get_model(self):
        return Vouchers

    def get_updated_field(self):
        return "modified"

    def index_queryset(self, using='default'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(modified__lte=datetime.datetime.now())


class AutoCompleteIndex(SimpleSearchIndex):
    """Defines an index and all fields should have autocomplete capabilities
    in the GUI.

    :param indexes.SearchIndex:
    :param indexes.Indexable:
    """
    text = indexes.EdgeNgramField(document=True, use_template=True)
    author = indexes.EdgeNgramField(model_attr='author', null=True)

    country = indexes.EdgeNgramField(model_attr='country', null=True)
    specific_locality = indexes.EdgeNgramField(model_attr='specific_locality', null=True)

    voucher_locality = indexes.EdgeNgramField(model_attr='voucher_locality', null=True)
    collector = indexes.EdgeNgramField(model_attr='collector', null=True)
    code_bold = indexes.EdgeNgramField(model_attr='code_bold', null=True)
    voucher_code = indexes.EdgeNgramField(model_attr='voucher_code', null=True)
    determined_by = indexes.EdgeNgramField(model_attr='determined_by', null=True)

    extraction = indexes.EdgeNgramField(model_attr='extraction', null=True)
    extraction_tube = indexes.EdgeNgramField(model_attr='extraction_tube', null=True)
    extractor = indexes.EdgeNgramField(model_attr='extractor', null=True)

    published_in = indexes.EdgeNgramField(model_attr='published_in', null=True)
    notes = indexes.EdgeNgramField(model_attr='notes', null=True)

    def get_updated_field(self):
        return "modified"

    def index_queryset(self, using='autocomplete'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(modified__lte=datetime.datetime.now())


class VouchersIndex(indexes.SearchIndex, indexes.Indexable):
    """We want extract matches for most fields. No partial match.
    """
    text = indexes.CharField(document=True, use_template=True)
    code = indexes.CharField(model_attr='code')
    orden = indexes.CharField(model_attr='orden')
    superfamily = indexes.CharField(model_attr='superfamily')
    family = indexes.CharField(model_attr='family')
    subfamily = indexes.CharField(model_attr='subfamily')
    tribe = indexes.CharField(model_attr='tribe')
    subtribe = indexes.CharField(model_attr='subtribe')
    genus = indexes.CharField(model_attr='genus')
    species = indexes.CharField(model_attr='species')
    subspecies = indexes.CharField(model_attr='subspecies')
    author = indexes.CharField(model_attr='author')

    country = indexes.CharField(model_attr='country')
    specific_locality = indexes.EdgeNgramField(
        model_attr='specific_locality',
        null=True,
    )

    voucher_locality = indexes.CharField(model_attr='voucher_locality')
    collector = indexes.CharField(model_attr='collector')
    code_bold = indexes.CharField(model_attr='code_bold')
    voucher_code = indexes.CharField(model_attr='voucher_code')
    determined_by = indexes.CharField(model_attr='determined_by')
    voucher = indexes.CharField(model_attr='voucher')
    date_collection = indexes.CharField(model_attr='date_collection')
    sex = indexes.CharField(model_attr='sex')

    extraction = indexes.CharField(model_attr='extraction')
    extraction_tube = indexes.CharField(model_attr='extraction_tube')
    extractor = indexes.CharField(model_attr='extractor')
    date_extraction = indexes.DateField(model_attr='date_extraction', null=True)

    published_in = indexes.EdgeNgramField(model_attr='published_in', null=True)
    notes = indexes.EdgeNgramField(model_attr='notes', null=True)
    hostorg = indexes.CharField(model_attr='hostorg')
    type_species = indexes.CharField(model_attr='type_species')

    def get_model(self):
        return Vouchers

    def get_updated_field(self):
        return "modified"

    def index_queryset(self, using='vouchers'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(modified__lte=datetime.datetime.now())


class AdvancedSearchIndex(indexes.SearchIndex, indexes.Indexable):
    """We also need some fields from our Sequences model.
    """
    # text = indexes.EdgeNgramField(document=True, use_template=True)
    text = indexes.CharField(document=True, use_template=True)
    code = indexes.CharField(model_attr='code__code', faceted=True)
    lab_person = indexes.EdgeNgramField(model_attr='lab_person', null=True)
    accession = indexes.EdgeNgramField(model_attr='accession', null=True)
    gene_code = indexes.CharField(model_attr='gene_code')
    genbank = indexes.BooleanField(model_attr='genbank', null=True)

    def get_model(self):
        return Sequences

    def get_updated_field(self):
        return "time_edited"

    def index_queryset(self, using='advanced_search'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(time_created__lte=datetime.datetime.now())
