from django.shortcuts import render
from django.http import HttpResponseRedirect

from core.utils import get_version_stats
from core.utils import get_username
from .utils import BLASTNew
from .forms import BLASTNewForm


def index(request):
    version, stats = get_version_stats()
    username = get_username(request)

    form = BLASTNewForm()
    return render(request, 'blast_new/index.html',
                  {
                      'username': username,
                      'form': form,
                      'version': version,
                      'stats': stats,
                  },
                  )


def results(request):
    version, stats = get_version_stats()
    username = get_username(request)

    if request.method == 'POST':
        form = BLASTNewForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            blast = BLASTNew('new', cleaned_data['name'], cleaned_data['sequence'],
                             cleaned_data['gene_codes'])
            blast.save_seqs_to_file()

            if blast.is_blast_db_up_to_date() is False:
                blast.create_blast_db()

            blast.save_query_to_file()
            blast.do_blast()
            result = blast.parse_blast_output()
            if len(result) < 1:
                result = None
            blast.delete_query_output_files()
            return render(request, 'blast_new/results.html',
                          {
                              'username': username,
                              'result': result,
                              'version': version,
                              'stats': stats,
                          },
                          )
        else:
            return render(request, 'blast_new/index.html',
                          {
                              'username': username,
                              'form': form,
                              'version': version,
                              'stats': stats,
                          },
                          )

    return HttpResponseRedirect('/blast_new/')
