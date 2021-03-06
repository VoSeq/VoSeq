import copy
import csv
import logging
import os
import uuid

from django.shortcuts import render
from django.http import HttpResponse
from amas import AMAS

from .forms import GeneTableForm
from core.utils import get_context, get_voucher_codes, get_gene_codes
from create_dataset.utils import CreateDataset
from public_interface.models import Genes


log = logging.getLogger(__name__)


def index(request):
    form = GeneTableForm()
    context = get_context(request)
    context["form"] = form
    return render(request, 'gene_table/index.html', context)


def results(request):
    context = get_context(request)
    if request.method == 'POST':
        form = GeneTableForm(request.POST)
        if form.is_valid():
            table = GeneTable(form.cleaned_data)
            response = create_excel_file(table.stats)
            return response

    context["form"] = GeneTableForm()
    return render(request, 'gene_table/index.html', context)


class GeneTable(object):
    def __init__(self, cleaned_data):
        self.cleaned_data = self.populate_cleaned_data_form(cleaned_data)
        self.voucher_codes = get_voucher_codes(cleaned_data)
        self.gene_codes = get_gene_codes(cleaned_data)
        self.fasta_datasets = self.get_fasta_datasets()
        self.genes_type = self.get_genes_type()
        self.stats = self.get_stats_from_datasets()

    def populate_cleaned_data_form(self, cleaned_data):
        cleaned_data['number_genes'] = None
        cleaned_data['aminoacids'] = False
        cleaned_data['translations'] = False
        cleaned_data['positions'] = ['ALL']
        cleaned_data['file_format'] = 'FASTA'
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['taxon_names'] = ['CODE', 'GENUS', 'SPECIES']
        cleaned_data['outgroup'] = ''
        return cleaned_data

    def get_fasta_datasets(self):
        fasta_datasets = []
        for gene_code in self.gene_codes:
            cleaned_data = copy.copy(self.cleaned_data)
            cleaned_data['geneset'] = None
            cleaned_data['gene_codes'] = [Genes.objects.get(gene_code=gene_code)]
            fasta = CreateDataset(cleaned_data)
            fasta_datasets.append(fasta)
        return fasta_datasets

    def get_genes_type(self):
        genes = Genes.objects.all().values('gene_code', 'gene_type')
        genes_dict = {}
        for gene in genes:
            gene_code = gene['gene_code']
            gene_type = gene['gene_type']
            genes_dict[gene_code] = gene_type
        return genes_dict

    def get_stats_from_datasets(self):
        """These are the stats headers of AMAS v0.2
        """
        stats = {}
        in_file = self.make_guid() + '.fas'

        for dataset in self.fasta_datasets:
            code = dataset.gene_codes[0]
            with open(in_file, 'w') as handle:
                handle.write(dataset.dataset_str)

            aln = AMAS.DNAAlignment(in_file, 'fasta', 'dna')
            aln_stats = aln.summarize_alignment()

            freq_summary = aln.get_freq_summary()[1][0:4]
            aln_stats += freq_summary
            aln_stats.append(code)

            this_stat = {
                'data_type': self.genes_type[code],
                'number_of_taxa': aln_stats[1],
                'alignment_length': aln_stats[2],
                'total_matrix_cells': aln_stats[3],
                'undetermined_chars': aln_stats[4],
                'missing_percent': aln_stats[5],
                'number_variable_sites': aln_stats[6],
                'proportion_variable_sites': aln_stats[7],
                'parsimony_informative_sites': aln_stats[8],
                'proportion_parsimony_informative': aln_stats[9],
                'freq_a': aln_stats[10],
                'freq_c': aln_stats[11],
                'freq_g': aln_stats[12],
                'freq_t': aln_stats[13],
            }
            stats[code] = this_stat

            try:
                os.remove(in_file)
            except OSError as e:
                log.error("There is no partition file to remove: {0}".format(e))
        return stats

    def make_guid(self):
        return uuid.uuid4().hex


def create_excel_file(stats):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gene_table.csv"'

    writer = csv.writer(response)

    row = ['Data set', 'Data type', 'Length', 'Dataset completion (%)', 'Variable (%)',
           'Pars. Inf. (%)', 'Conserved (%)', 'Freq. A (%)', 'Freq. T/U (%)', 'Freq. C (%)',
           'Freq. G (%)', 'Introns (n)', 'Tot. intron length (bp)']
    writer.writerow(row)
    for gene in stats:
        this_stats = stats[gene]
        row = [gene]
        row.append(this_stats['data_type'])
        row.append(this_stats['alignment_length'])
        row.append(100 - float(this_stats['missing_percent']))
        row.append(float(this_stats['proportion_variable_sites']) * 100)
        row.append(this_stats['proportion_parsimony_informative'])
        row.append(100 - (float(this_stats['proportion_variable_sites']) * 100))
        row.append(float(this_stats['freq_a']) * 100)
        row.append(float(this_stats['freq_t']) * 100)
        row.append(float(this_stats['freq_c']) * 100)
        row.append(float(this_stats['freq_g']) * 100)
        writer.writerow(row)
    return response
