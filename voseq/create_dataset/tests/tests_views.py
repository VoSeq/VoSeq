from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from public_interface.models import Genes


class CreateDatasetViewsTest(TestCase):
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
        }

        self.c = Client()

    def test_view_index(self):
        res = self.c.get('/create_dataset/')
        self.assertEqual(200, res.status_code)

    def test_view_result(self):
        res = self.c.post('/create_dataset/results/',
                          {
                              'voucher_codes': None,
                              'gene_codes': [],
                              'geneset': 1,
                              'taxonset': 1,
                              'introns': 'YES',
                              'positions': 'ALL',
                              'translations': False,
                              'partition_by_positions': 'ONE',
                              'file_format': 'FASTA',
                              'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
                              'degen_translations': 'NORMAL',
                              'exclude': 'YES',
                              'aminoacids': False,
                              'outgroup': '',
                              'special': False,
                          }
                          )
        self.assertEqual(200, res.status_code)

    def test_view_result_invalid_form(self):
        res = self.c.post('/create_dataset/results/',
                          {
                              'voucher_codes': None,
                              'gene_codes': [],
                              'geneset': 1,
                              'taxonset': 1,
                          }
                          )
        self.assertEqual(200, res.status_code)

    def test_view_result_get(self):
        res = self.c.get('/create_dataset/results/')
        self.assertEqual(302, res.status_code)
