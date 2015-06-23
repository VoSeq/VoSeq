from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import VoucherTableForm
from .utils import VoucherTable
from core.utils import get_version_stats
from core.utils import get_username


def index(request):
    version, stats = get_version_stats()
    username = get_username(request)
    form = VoucherTableForm()

    return render(request, 'voucher_table/index.html',
                  {
                      'username': username,
                      'version': version,
                      'stats': stats,
                      'form': form,
                  },
                  )


def results(request):
    if request.method == 'POST':
        form = VoucherTableForm(request.POST)
        if form.is_valid():
            table = VoucherTable(form.cleaned_data)
            response = table.create_csv_file()
            return response

    return HttpResponseRedirect('/create_voucher_table/')
