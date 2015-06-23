from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from create_dataset.utils import CreateDataset
from public_interface.models import Genes


class CreateMEGADatasetTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        g1 = Genes.objects.get(gene_code='COI')
        g2 = Genes.objects.get(gene_code='EF1a')
        self.cleaned_data = {
            'gene_codes': [g1, g2],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': None,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'number_genes': None,
            'positions': ['ALL'],
            'partition_by_positions': 'ONE',
            'file_format': 'MEGA',
            'aminoacids': False,
            'outgroup': '',
        }

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_headers(self):
        expected = '#MEGA\n!TITLE title;\n\n'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_sequence_line_breaks(self):
        expected = '#CP100-10_Melitaea_diamina\n?????????????????????????TGAGCCGGTATAATTGGTACAT'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_sequence_concatenation(self):
        expected = '??????????????????????????CAAGT'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)
