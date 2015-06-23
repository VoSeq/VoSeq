import os
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from core.utils import get_version_stats
from core.utils import get_username
from .forms import CreateDatasetForm
from .utils import CreateDataset


@login_required
def index(request):
    form = CreateDatasetForm()
    username = get_username(request)

    return render(request,
                  'create_dataset/index.html',
                  {
                      'username': username,
                      'form': form,
                  },
                  )


@login_required
def results(request):
    version, stats = get_version_stats()
    username = get_username(request)

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
                              'username': username,
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
                              'username': username,
                              'form': form,
                              'version': version,
                              'stats': stats,
                          },
                          )
    else:
        return HttpResponseRedirect('/create_dataset/')


@login_required
def serve_file(request, file_name):
    final_name = guess_file_extension(file_name)
    cwd = os.path.dirname(__file__)
    dataset_file = os.path.join(cwd,
                                'dataset_files',
                                file_name,
                                )
    if os.path.isfile(dataset_file):
        response = HttpResponse(open(dataset_file, 'r').read(), content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename={}'.format(final_name)
        os.remove(dataset_file)
        return response
    else:
        return render(request, 'create_dataset/missing_file.html')


def guess_file_extension(file_name):
    try:
        prefix = re.search('^(\w+)\_', file_name).group()
    except AttributeError:
        return file_name

    if prefix == 'MEGA_':
        extension = 'meg'
    else:
        return file_name

    name = file_name.replace('.txt', '')
    return '{}.{}'.format(name, extension)
