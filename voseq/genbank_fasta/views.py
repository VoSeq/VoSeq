import os
import json
import re

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from core.utils import get_version_stats
from .forms import GenBankFastaForm
from . import utils


def index(request):
    version, stats = get_version_stats()

    form = GenBankFastaForm()
    return render(request,
                  'genbank_fasta/index.html',
                  {
                      'form': form,
                      'version': version,
                      'stats': stats,
                  },
                  )


def results(request):
    version, stats = get_version_stats()

    if request.method == 'POST':
        form = GenBankFastaForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            voucher_codes = utils.get_voucher_codes(cleaned_data)
            gene_codes = utils.get_gene_codes(cleaned_data)

            res = utils.Results(voucher_codes, gene_codes)
            res.get_datasets()
            items_with_accession = res.items_with_accession
            fasta = res.fasta
            protein = res.protein
            fasta_file = re.search('(fasta_[a-z0-9]+\.fasta)', res.fasta_file).groups()[0]
            protein_file = re.search('(prot_[a-z0-9]+\.fasta)', res.protein_file).groups()[0]

            return render(request, 'genbank_fasta/results.html',
                          {
                              'items_with_accession': items_with_accession,
                              'fasta': fasta,
                              'fasta_file': fasta_file,
                              'protein': protein,
                              'protein_file': protein_file,
                              'version': version,
                              'stats': stats,
                          },
                          )
        else:
            return render(request, 'genbank_fasta/index.html',
                          {
                              'form': form,
                              'version': version,
                              'stats': stats,
                          },
                          )

    return HttpResponseRedirect('/genbank_fasta/')


def serve_file(request, file_name):
    cwd = os.path.dirname(__file__)
    fasta_file = os.path.join(cwd,
                              'fasta_files',
                              file_name,
                              )
    response = HttpResponse(open(fasta_file, 'r').read(), content_type='application/text')
    response['Content-Disposition'] = 'attachment; filename=voseq_genbank.fasta'

    if os.path.isfile(fasta_file):
        os.remove(fasta_file)
    return response
