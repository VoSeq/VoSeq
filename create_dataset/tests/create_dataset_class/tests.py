from django.test import TestCase

from public_interface.models import Genes
from public_interface.models import Sequences
from public_interface.models import GeneSets
from public_interface.models import Vouchers
from public_interface.models import TaxonSets
from create_dataset.utils import CreateDataset


class TestCreateDataset(TestCase):
    def setUp(self):
        self.maxDiff = None
        genes = ['abc1', 'BC1', 'ABC2', 'CC', 'xaz', 'XYZ']
        GeneSets(geneset_name='6genes', geneset_creator='Carlos Pena',
                 geneset_list="\n".join(genes)).save()

        taxa = ['CP100-10', 'CP100-11', 'CP100-12']
        TaxonSets(taxonset_name='all_taxa', taxonset_creator='Carlos Pena',
                  taxonset_list="\n".join(taxa)).save()

        tmp = []
        for taxon in taxa:
            tmp.append(Vouchers(code=taxon))
        Vouchers.objects.bulk_create(tmp)

        tmp = []
        for gene in genes:
            tmp.append(Genes(gene_code=gene, genetic_code=1, length=600,
                             reading_frame=1))
        Genes.objects.bulk_create(tmp)

        for gene in genes:
            for taxon in taxa:
                voucher = Vouchers.objects.get(code=taxon)
                gene_obj = Genes.objects.get(gene_code=gene)
                Sequences(code=voucher, gene=gene_obj, sequences='ACTG',
                          genbank=False).save()

        self.cleaned_data = {
            'voucher_codes': '',
            'positions': ['ALL'],
            'introns': 'YES',
            'gene_codes': [],
            'partition_by_positions': 'by gene',
            'number_genes': None,
            'geneset': GeneSets.objects.get(geneset_name='6genes'),
            'file_format': 'PHY',
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'special': False,
            'taxonset': TaxonSets.objects.get(taxonset_name='all_taxa'),
            'outgroup': '',
            'aminoacids': False,
            'translations': False,
            'degen_translations': 'NORMAL'
        }

    def test_seq_objs_have_sorted_gene_codes(self):
        result = CreateDataset(self.cleaned_data)
        self.assertEqual(['abc1', 'ABC2', 'BC1', 'CC', 'xaz', 'XYZ'],
                         list(result.gene_codes))

    def test_warning_when_missing_seqs_for_voucher(self):
        Vouchers(code='CP100-13').save()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['voucher_codes'] = 'CP100-13'

        expected = 'Could not find sequences for voucher CP100-13 and gene_code CC'
        result = CreateDataset(cleaned_data)

        self.assertTrue(expected in result.warnings)
