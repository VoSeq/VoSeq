from django.http import Http404
from django.shortcuts import render
from django.conf import settings

from core.utils import get_version_stats
from .models import Vouchers
from .models import FlickrImages
from .models import Sequences
from .models import Primers
from .forms import AdvancedSearchForm


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
    version, stats = get_version_stats()

    if request.method == 'GET' and bool(request.GET) is not False:
        form = AdvancedSearchForm(request.GET)
        if form.is_valid():
            # do search
            results = form.search()
            if results:
                return render(request, 'public_interface/search_results.html',
                              {
                                  'form': form,
                                  'results': results,
                                  'version': version,
                                  'stats': stats,
                              })
            else:
                return render(request, 'public_interface/search.html',
                              {
                                  'form': form,
                                  'results': 'No results',
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

    seqs_queryset = Sequences.objects.filter(code=voucher_code).order_by('gene_code')
    for item in seqs_queryset:
        seq = item.sequences
        item.sequence_length = len(seq)
        item.ambiguous_seq_length = seq.count('?') + seq.count('-') + seq.count('N') + seq.count('n')
        if item.labPerson is not None:
            item.labPerson = item.labPerson.split(" ")[0]

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
