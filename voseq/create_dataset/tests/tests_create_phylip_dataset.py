from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.contrib.auth.models import User

from create_dataset.utils import CreateDataset
from public_interface.models import Genes


class CreatePhylipDatasetTest(TestCase):
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
            'file_format': 'PHY',
            'aminoacids': True,
            'outgroup': '',
        }

        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_create_dataset(self):
        expected = '2 761\nCP100-10_Melitaea_diamina'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_only_one_set_of_taxon_names(self):
        expected = 1
        dataset = self.dataset_creator.dataset_str
        result = dataset.count('CP100-10_Melitaea_diamina')
        self.assertEqual(expected, result)

    def test_stop_codon_warning(self):
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.c.post('/create_dataset/results/',
                        {
                            'voucher_codes': '',
                            'gene_codes': [],
                            'geneset': 1,
                            'taxonset': 1,
                            'translations': False,
                            'introns': 'YES',
                            'file_format': 'PHY',
                            'degen_translations': 'NORMAL',
                            'exclude': 'YES',
                            'aminoacids': True,
                            'special': False,
                            'outgroup': '',
                            'positions': 'ALL',
                            'partition_by_positions': 'ONE',
                            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
                        }
                        )
        expected = 'stop'
        result = str(c.content)
        self.assertTrue(expected in result)

    def test_numer_of_chars_for_aa_dataset(self):
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.c.post('/create_dataset/results/',
                        {
                            'voucher_codes': 'CP100-10',
                            'gene_codes': 3,  # wingless
                            'geneset': '',
                            'taxonset': '',
                            'translations': False,
                            'introns': 'YES',
                            'file_format': 'PHY',
                            'degen_translations': 'NORMAL',
                            'exclude': 'YES',
                            'aminoacids': True,
                            'special': False,
                            'outgroup': '',
                            'positions': 'ALL',
                            'partition_by_positions': 'ONE',
                            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
                        }
                        )
        expected = '1 137'
        self.assertTrue(expected in str(c.content))
