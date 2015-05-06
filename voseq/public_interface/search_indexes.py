import datetime

from haystack import indexes

from .models import Vouchers
from .models import Sequences


class SimpleSearchIndex(indexes.SearchIndex, indexes.Indexable):
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

    # TODO change to time_edited, time_created with auto in tables and migrate_db script
    def index_queryset(self, using='default'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())


class AdvancedSearchIndex(SimpleSearchIndex):
    """Defines an index and all fields should have autocomplete capabilities
    in the GUI.

    :param indexes.SearchIndex:
    :param indexes.Indexable:
    :returns: class AdvancedSearchIndex
    """
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.EdgeNgramField(model_attr='author', null=True)

    country = indexes.EdgeNgramField(model_attr='country', null=True)
    specificLocality = indexes.EdgeNgramField(model_attr='specificLocality', null=True)

    voucherLocality = indexes.EdgeNgramField(model_attr='voucherLocality', null=True)
    collector = indexes.EdgeNgramField(model_attr='collector', null=True)
    code_bold = indexes.EdgeNgramField(model_attr='code_bold', null=True)
    voucherCode = indexes.EdgeNgramField(model_attr='voucherCode', null=True)
    determinedBy = indexes.EdgeNgramField(model_attr='determinedBy', null=True)

    extractor = indexes.EdgeNgramField(model_attr='extractor', null=True)

    publishedIn = indexes.EdgeNgramField(model_attr='publishedIn', null=True)
    notes = indexes.EdgeNgramField(model_attr='notes', null=True)

    def index_queryset(self, using='advanced_search'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(timestamp__lte=datetime.datetime.now())


class SequencesIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    labPerson = indexes.EdgeNgramField(model_attr='labPerson', null=True)

    def get_model(self):
        return Sequences

    def index_queryset(self, using='sequences'):
        # Used when the entire index for model is updated.
        return self.get_model().objects.filter(time_created__lte=datetime.datetime.now())
