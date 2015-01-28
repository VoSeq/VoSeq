from django.shortcuts import render
from django.http import HttpResponseRedirect

from core.utils import get_version_stats
from .forms import CreateDatasetForm


def index(request):
    form = CreateDatasetForm()

    return render(request,
                  'create_dataset/index.html',
                  {
                      'form': form,
                  },
                  )


def results(request):
    version, stats = get_version_stats()

    if request.method == 'POST':
        print(request.POST)
        form = CreateDatasetForm(request.POST)

        if form.is_valid():
            print(form)
            return render(request, 'create_dataset/results.html',
                          {
                              'version': version,
                              'stats': stats,
                          },
                          )
        else:
            print("invalid form")
            return render(request, 'create_dataset/index.html',
                          {
                              'form': form,
                              'version': version,
                              'stats': stats,
                          },
                          )
    else:
        return HttpResponseRedirect('/create_dataset/')
