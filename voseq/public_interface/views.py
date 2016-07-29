from itertools import chain
import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import Http404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings

from haystack.forms import SearchForm
from haystack.query import ValuesSearchQuerySet

from core.utils import get_version_stats
from core.utils import get_username
from .utils import VoSeqSearchView
from .models import Vouchers
from .models import FlickrImages
from .models import LocalImages
from .models import Sequences
from .models import Primers
from .forms import AdvancedSearchForm, BatchChangesForm


def index(request):
    version, stats = get_version_stats()
    username = get_username(request)

    return render(request,
                  'public_interface/index.html',
                  {
                      'username': username,
                      'version': version,
                      'stats': stats,
                  },
                  )


def browse(request):
    version, stats = get_version_stats()
    username = get_username(request)

    queryset = Vouchers.objects.order_by('-modified')[:10]

    vouchers_with_images = []
    # Lookups that span relationships
    #  https://docs.djangoproject.com/en/1.8/topics/db/queries/#lookups-that-span-relationships
    for i in Vouchers.objects.filter(flickrimages__voucher_id__isnull=False):
        vouchers_with_images.append(i.code)

    for i in Vouchers.objects.filter(localimages__voucher_id__isnull=False):
        vouchers_with_images.append(i.code)

    return render(request, 'public_interface/browse.html',
                  {
                      'username': username,
                      'results': queryset,
                      'vouchers_with_images': set(vouchers_with_images),
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
    username = get_username(request)

    if request.method == 'GET' and bool(request.GET) is not False:
        form = AdvancedSearchForm(request.GET)

        if form.is_valid():
            sqs = form.search()
            search_view = VoSeqSearchView(
                url_encoded_query=request.GET.urlencode(),
                template='public_interface/search_results.html',
                searchqueryset=sqs,
                form_class=AdvancedSearchForm,
            )

            if sqs is not None:
                search_view.__call__(request)
                search_view.query = sqs.query
                return search_view.create_response()
            else:
                return render(request, 'public_interface/search_results.html',
                              {
                                  'username': username,
                                  'form': form,
                                  'version': version,
                                  'stats': stats,
                              })
        else:
            return render(request, 'public_interface/search.html',
                          {
                              'username': username,
                              'form': form,
                              'version': version,
                              'stats': stats,
                          })
    else:
        form = AdvancedSearchForm()
        return render(request, 'public_interface/search.html',
                      {
                          'username': username,
                          'form': form,
                          'version': version,
                          'stats': stats,
                      })


def show_voucher(request, voucher_code):
    version, stats = get_version_stats()
    username = get_username(request)

    try:
        voucher_queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    flickr_images_queryset = FlickrImages.objects.filter(voucher=voucher_code)
    local_images_queryset = LocalImages.objects.filter(voucher=voucher_code)
    images_queryset = list(chain(flickr_images_queryset, local_images_queryset))

    seqs_queryset = Sequences.objects.filter(code=voucher_code).values(
        'code',
        'gene_code',
        'number_ambiguous_bp',
        'accession',
        'lab_person',
        'total_number_bp',
    )
    print(seqs_queryset)
    sorted_seqs_queryset = sorted(seqs_queryset, key=lambda x: x['gene_code'].lower())

    return render(request, 'public_interface/show_voucher.html',
                  {
                      'username': username,
                      'voucher': voucher_queryset,
                      'images': images_queryset,
                      'sequences': sorted_seqs_queryset,
                      'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
                      'version': version,
                      'stats': stats,
                  })


@login_required
def show_sequence(request, voucher_code, gene_code):
    version, stats = get_version_stats()
    username = get_username(request)

    try:
        queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    seqs_queryset = Sequences.objects.get(code=voucher_code, gene_code=gene_code)
    images_queryset = FlickrImages.objects.filter(voucher=voucher_code)
    primers_queryset = Primers.objects.filter(for_sequence=seqs_queryset)

    return render(request, 'public_interface/show_sequence.html',
                  {
                      'username': username,
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
