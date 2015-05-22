import json

from django.shortcuts import render
from django.http import HttpResponse

from core.utils import get_version_stats
from public_interface.models import Vouchers


def index(request):
    version, stats = get_version_stats()
    return render(request, 'gbif/index.html',
                  {
                      'version': version,
                      'stats': stats,
                  },
                  )


def dump_data(request):
    try:
        wanted = request.GET['request']
    except KeyError:
        msg = json.dumps({'result': 'error'})
        return HttpResponse(msg, content_type='application/json')
    print(request.GET)

    if wanted == 'count_data':
        the_data = get_data_count()
        msg = json.dumps({
            'result': True,
            'count': the_data,
        })
    return HttpResponse(msg, content_type='application/json')


def get_data_count():
    voucher_count = Vouchers.objects.count()
    return voucher_count


def results(request):
    return ''
