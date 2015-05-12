import json
import re

from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

from haystack.forms import SearchForm
from haystack.views import SearchView
from haystack.query import ValuesSearchQuerySet

from core.utils import get_version_stats
from .models import Vouchers
from .models import FlickrImages
from .models import Sequences
from .models import Primers
from .forms import AdvancedSearchForm, BatchChangesForm


def index(request):
    version, stats = get_version_stats()

    return render(request,
                  'public_interface/index.html',
                  {
                      'version': version,
                      'stats': stats,
                  },
                  )


def browse(request):
    version, stats = get_version_stats()

    queryset = Vouchers.objects.order_by('-timestamp')[:10]

    # TODO improve this ugly hack. Use select_related or prefetch_related
    vouchers_with_images = []
    for i in queryset:
        q = FlickrImages.objects.filter(voucher=i.code)
        if q.count() > 0:
            vouchers_with_images.append(i.code)

    return render(request, 'public_interface/browse.html',
                  {
                      'results': queryset,
                      'vouchers_with_images': vouchers_with_images,
                      'version': version,
                      'stats': stats,
                  },
                  )


def search(request):
    """Simple search tool"""
    if 'q' not in request.GET:
        return redirect('/')

    query = request.GET['q'].strip()
    if query == '':
        return redirect('/')

    form = SearchForm(request.GET)
    sqs = form.search()
    sqs.spelling_suggestion()

    search_view = VoSeqSearchView(
        template='public_interface/search_results.html',
        searchqueryset=sqs,
        form_class=SearchForm,
        url_encoded_query=request.GET.urlencode(),
    )
    search_view.__call__(request)
    return search_view.create_response()


class VoSeqSearchView(SearchView):
    def __init__(self, url_encoded_query, *args, **kwargs):
        self.url_encoded_query = self.get_correct_url_query(url_encoded_query)
        self.simple_query = self.recover_keyword(url_encoded_query)
        super(VoSeqSearchView, self).__init__(*args, **kwargs)

    def get_correct_url_query(self, url_encoded_query):
        this_query = self.strip_page(url_encoded_query)
        return this_query

    def recover_keyword(self, url_encoded_query):
        this_query = re.sub('\w+=Select', ' ', url_encoded_query)
        this_query = re.sub('\w+=', ' ', this_query)
        this_query = this_query.replace('&', ' ')
        this_query = re.sub('\s+', ' ', this_query)
        return this_query.strip()

    def strip_page(self, url_encoded_query):
        this_query = re.sub('page=[0-2]+', '', url_encoded_query)
        this_query = this_query.replace('&&', '&')
        this_query = re.sub('^&', '', this_query)
        this_query = re.sub('&$', '', this_query)
        return this_query

    def extra_context(self):
        version, stats = get_version_stats()
        return {
            'simple_query': self.simple_query,
            'url_encoded_query': self.url_encoded_query,
            'result_count': len(self.searchqueryset),
            'version': version,
            'stats': stats,
        }


def autocomplete(request):
    """Used for JSON queries from javascript to fill autocomplete values in
    input boxes of advanced searches.

    :param request:
    :return:
    """
    try:
        field = request.GET['field']
    except KeyError:
        raise Http404("Value for <b>field</b> is missing.")

    try:
        term = request.GET['term']
    except KeyError:
        raise Http404("Value for <b>term</b> query is missing.")

    field_term = {field: term}
    sqs = ValuesSearchQuerySet().using('autocomplete').autocomplete(**field_term).values(field)[:5]

    suggestions = set()
    for result in sqs:
        suggestions.add(result[field])
    suggestions = list(suggestions)

    the_data = json.dumps(suggestions)
    return HttpResponse(the_data, content_type='application/json')


def search_advanced(request):
    """Uses the haystack index `advanced_search` to find values based on a
    combination of queries for one or more fields.
    Works in a similar way to **genus:Mopho AND species:helenor**

    :param request: HTTP request from the url dispatcher.
    :return: response to html template.
    """
    version, stats = get_version_stats()

    if request.method == 'GET' and bool(request.GET) is not False:
        form = AdvancedSearchForm(request.GET)

        if form.is_valid():
            sqs = form.search()
            search_view = VoSeqSearchView(
                url_encoded_query=request.GET.urlencode(),
                template='public_interface/search_results.html',
                searchqueryset=sqs,
                form_class=AdvancedSearchForm
            )

            if sqs is not None:
                search_view.__call__(request)
                search_view.query = sqs.query
                return search_view.create_response()
            else:
                return render(request, 'public_interface/search_results.html',
                              {
                                  'form': form,
                                  'version': version,
                                  'stats': stats,
                              })
        else:
            return render(request, 'public_interface/search.html',
                          {
                              'form': form,
                              'version': version,
                              'stats': stats,
                          })
    else:
        form = AdvancedSearchForm()
        return render(request, 'public_interface/search.html',
                      {
                          'form': form,
                          'version': version,
                          'stats': stats,
                      })


def show_voucher(request, voucher_code):
    version, stats = get_version_stats()

    try:
        voucher_queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    images_queryset = FlickrImages.objects.filter(voucher=voucher_code)

    seqs_queryset = Sequences.objects.filter(code=voucher_code).values('code', 'gene_code',
                                                                       'number_ambiguous_bp',
                                                                       'accession', 'labPerson')

    return render(request, 'public_interface/show_voucher.html',
                  {'voucher': voucher_queryset,
                   'images': images_queryset,
                   'sequences': seqs_queryset,
                   'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
                   'version': version,
                   'stats': stats,
                   },
                  )


def show_sequence(request, voucher_code, gene_code):
    version, stats = get_version_stats()

    try:
        queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    seqs_queryset = Sequences.objects.get(code=voucher_code, gene_code=gene_code)
    images_queryset = FlickrImages.objects.filter(voucher=voucher_code)
    primers_queryset = Primers.objects.filter(for_sequence=seqs_queryset)

    return render(request, 'public_interface/show_sequence.html',
                  {
                      'voucher': queryset,
                      'sequence': seqs_queryset,
                      'images': images_queryset,
                      'primers': primers_queryset,
                      'version': version,
                      'stats': stats,
                  },)


@csrf_protect
def change_selected(request, selected):
    """
    Changes field values from Vouchers in batch.

    This action first displays a change form page whichs shows all the
    fields of a Vouchers type.
    Next, it changes all selected objects and redirects back to the changed list.

    The action that calls this function should raise a PermissionDenied
    if the user has no rights for changes.
    """

    # The user has already proposed the changes.
    # Apply the changes and return a None to display the changed list.

    if request.method == 'POST':
        form = BatchChangesForm(request.POST)
        ids = selected.split(",")
        queryset = Vouchers.objects.filter(pk__in=ids)
        n = queryset.count()

        if n and form.is_valid():
            # do changes
            keywords = {}
            for field, value in form.cleaned_data.items():
                if value:
                    keywords[field] = value

            queryset.update(**keywords)

            return HttpResponseRedirect('/admin/public_interface/vouchers/')

    else:
        form = BatchChangesForm()

    # Display the changes page
    context = {'form': form, 'selected': selected}
    return render(request, 'admin/public_interface/vouchers/batch_changes.html', context)
