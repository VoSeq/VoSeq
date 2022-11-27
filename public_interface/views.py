from itertools import chain
import json
import logging

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.conf import settings

from haystack.forms import SearchForm
from haystack.query import ValuesSearchQuerySet

from core.utils import get_context
from .utils import get_simple_query, get_correct_url_query, get_voucher_code_list
from public_interface.models import Vouchers, FlickrImages, LocalImages, Sequences, Primers
from .forms import AdvancedSearchForm, BatchChangesForm


log = logging.getLogger(__name__)


def index(request):
    context = get_context(request)
    return render(request, 'public_interface/index.html', context)


def browse(request):
    context = get_context(request)
    queryset = Vouchers.objects.order_by('-modified')[:10]

    vouchers_with_images = []
    # Lookups that span relationships
    #  https://docs.djangoproject.com/en/1.8/topics/db/queries/#lookups-that-span-relationships
    for i in Vouchers.objects.filter(flickrimages__voucher_id__isnull=False):
        vouchers_with_images.append(i.code)

    for i in Vouchers.objects.filter(localimages__voucher_id__isnull=False):
        vouchers_with_images.append(i.code)

    context["results"] = queryset
    context['vouchers_with_images'] = set(vouchers_with_images)
    return render(request, 'public_interface/browse.html', context)


def search(request):
    """Simple search tool"""
    context = get_context(request)
    context['simple_query'] = get_simple_query(request)

    if 'q' not in request.GET:
        return redirect('/')

    query = request.GET['q'].strip()
    if query == '':
        return redirect('/')

    page = request.GET.get('page')

    sqs = Vouchers.objects.filter(
        Q(orden__icontains=query) |
        Q(genus__icontains=query) | Q(species__icontains=query) | Q(code__icontains=query),
    )
    results = ""
    paginator = ""
    if sqs:
        paginator = Paginator(sqs, 25)
        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            results = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            results = paginator.page(paginator.num_pages)
    context["result_count"] = sqs.count()
    context['page'] = results
    context['paginator'] = paginator
    context['results'] = results
    return render(request, 'public_interface/search_results.html', context)


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
    context = get_context(request)
    context["is_advanced_search"] = True

    if request.method == 'GET' and bool(request.GET) is not False:
        form = AdvancedSearchForm(request.GET)

        page = request.GET.get('page')
        if form.is_valid():
            sqs = form.search()
            results = ""
            paginator = ""
            if sqs:
                paginator = Paginator(sqs, 25)
                try:
                    results = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    results = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    results = paginator.page(paginator.num_pages)
            if sqs is not None:
                context['page'] = results
                context['paginator'] = paginator
                context['results'] = results
                context['voucher_code_list'] = get_voucher_code_list(sqs)
                context['simple_query'] = get_simple_query(request)
                context['url_encoded_query'] = get_correct_url_query(request.GET.urlencode())
                context['result_count'] = len(sqs)
                return render(request, 'public_interface/search_results.html', context)
            else:
                context["form"] = form
                return render(request, 'public_interface/search_results.html', context)
        else:
            context["form"] = form
            return render(request, 'public_interface/search.html', context)
    else:
        form = AdvancedSearchForm()
        context["form"] = form
        return render(request, 'public_interface/search.html', context)


def show_voucher(request, voucher_code):
    context = get_context(request)

    try:
        voucher_queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    flickr_images_queryset = FlickrImages.objects.filter(voucher=voucher_code)
    local_images_queryset = LocalImages.objects.filter(voucher=voucher_code)
    images_queryset = list(chain(flickr_images_queryset, local_images_queryset))

    seqs_queryset = Sequences.objects.filter(code=voucher_queryset).order_by('gene__gene_code')

    context['voucher'] = voucher_queryset
    context['images'] = images_queryset
    context['sequences'] = seqs_queryset
    context['google_maps_api_key'] = settings.GOOGLE_MAPS_API_KEY
    return render(request, 'public_interface/show_voucher.html', context)


@login_required
def show_sequence(request, voucher_code, gene_code):
    context = get_context(request)

    try:
        queryset = Vouchers.objects.get(code__iexact=voucher_code)
    except Vouchers.DoesNotExist:
        raise Http404

    seqs_queryset = Sequences.objects.filter(
        code=voucher_code, gene__gene_code=gene_code
    ).first()
    images_queryset = FlickrImages.objects.filter(voucher=voucher_code)
    primers_queryset = Primers.objects.filter(for_sequence=seqs_queryset)

    context['voucher'] = queryset
    context['sequence'] = seqs_queryset
    context['images'] = images_queryset
    context['primers'] = primers_queryset

    return render(request, 'public_interface/show_sequence.html', context)


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
