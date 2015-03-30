import os
import re

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

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
            print(">>>>", form.cleaned_data)
            dataset_creator = CreateDataset(form.cleaned_data)
            dataset = dataset_creator.dataset_str[0:1500] + '\n...\n\n\n' + '#######\nComplete dataset file available for download.\n#######'
            errors = dataset_creator.errors
            warnings = dataset_creator.warnings

            dataset_file_abs = dataset_creator.dataset_file
            if dataset_file_abs is not None:
                dataset_file = re.search('([A-Z]+_[a-z0-9]+\.txt)', dataset_file_abs).groups()[0]
            else:
                dataset_file = False

            return render(request, 'create_dataset/results.html',
                          {
                              'dataset_file': dataset_file,
                              'charset_block': dataset_creator.charset_block,
                              'dataset': dataset,
                              'errors': errors,
                              'warnings': warnings,
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


def serve_file(request, file_name):
    cwd = os.path.dirname(__file__)
    dataset_file = os.path.join(cwd,
                                'dataset_files',
                                file_name,
                                )
    if os.path.isfile(dataset_file):
        response = HttpResponse(open(dataset_file, 'r').read(), content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename=dataset_file.txt'
        os.remove(dataset_file)
        return response
    else:
        return render(request, 'create_dataset/missing_file.html')
