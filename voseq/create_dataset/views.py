from django.shortcuts import render
from django.http import HttpResponseRedirect

from core.utils import get_version_stats
from .forms import CreateDatasetForm
from .utils import CreateDataset


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
        form = CreateDatasetForm(request.POST)

        if form.is_valid():
            dataset_creator = CreateDataset(form.cleaned_data)
            dataset = dataset_creator.dataset_str
            errors = dataset_creator.errors
            return render(request, 'create_dataset/results.html',
                          {
                              'dataset': dataset,
                              'errors': errors,
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
