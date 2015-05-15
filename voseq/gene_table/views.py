from collections import OrderedDict

from django.shortcuts import render

from .forms import GeneTableForm
from core.utils import get_version_stats
from core.utils import get_voucher_codes
from core.utils import get_gene_codes
from create_dataset.utils import CreateDataset


def index(request):
    form = GeneTableForm()

    return render(request, 'gene_table/index.html',
                  {
                      'form': form,
                  },
                  )


def results(request):
    version, stats = get_version_stats()
    if request.method == 'POST':
        form = GeneTableForm(request.POST)
        if form.is_valid():
            print(">>>>", form.cleaned_data)
            table = GeneTable(form.cleaned_data)
            return render(request, 'gene_table/results.html',
                          {
                              'version': version,
                              'stats': stats,
                          },
                          )


class GeneTable(object):
    def __init__(self, cleaned_data):
        self.cleaned_data = self.populate_cleaned_data_form(cleaned_data)
        self.voucher_codes = get_voucher_codes(cleaned_data)
        self.gene_codes = get_gene_codes(cleaned_data)
        self.fasta_dataset = self.get_fasta_dataset()
        self.fasta_partitions = self.split_in_partitions()
        self.stats = self.get_stats_from_partitions()

    def populate_cleaned_data_form(self, cleaned_data):
        cleaned_data['number_genes'] = None
        cleaned_data['aminoacids'] = False
        cleaned_data['positions'] = ['ALL']
        cleaned_data['file_format'] = 'FASTA'
        cleaned_data['partition_by_positions'] = 'ONE'
        cleaned_data['taxon_names'] = ['CODE', 'GENUS', 'SPECIES']
        cleaned_data['outgroup'] = ''
        return cleaned_data

    def get_fasta_dataset(self):
        fasta = CreateDataset(self.cleaned_data)
        return fasta.dataset_str

    def split_in_partitions(self):
        partitions = OrderedDict()

        lines = self.fasta_dataset.split('\n')
        for line in lines:
            this_line = line.replace('>', '')
            if this_line in self.gene_codes:
                this_gene = this_line
                partitions[this_gene] = ''
            elif this_line.startswith('---------------'):
                continue
            else:
                partitions[this_gene] += line

        return partitions

    def get_stats_from_partitions(self):
        pass
