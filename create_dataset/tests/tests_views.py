from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.client import Client

from create_dataset.models import Dataset
from create_dataset.tasks import create_dataset
from public_interface.models import Genes, Sequences, Vouchers
from django.contrib.auth.models import User


class CreateDatasetViewsTest(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("alter sequence public_interface_genesets_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_taxonsets_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_sequences_id_seq restart with 1")
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.g1 = Genes.objects.get(gene_code='COI-begin')
        g2 = Genes.objects.get(gene_code='ef1a')
        self.cleaned_data = {
            'gene_codes': [self.g1, g2],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': None,
            'outgroup': '',
        }

        self.c = Client()
        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()
        self.maxDiff = None

    def test_view_index(self):
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        res = self.c.get('/create_dataset/')
        self.assertEqual(200, res.status_code)

    def test_create_dataset(self):
        dataset_obj = Dataset.objects.create()
        create_dataset(
            taxonset_id=1,
            geneset_id=1,
            gene_codes_ids=[],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by codon position',
            translations=False,
            aminoacids=False,
            degen_translations='NORMAL',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        expected = 'ACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACG'
        self.assertIn(expected, dataset_obj.content)

    def test_view_result_invalid_form(self):
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        res = self.c.post('/create_dataset/results/',
                          {
                              'voucher_codes': '',
                              'gene_codes': [],
                              'geneset': 1,
                              'taxonset': 1,
                          }
                          )
        self.assertEqual(200, res.status_code)

    def test_view_result_get(self):
        res = self.c.get('/create_dataset/results/')
        self.assertEqual(302, res.status_code)

    def test_create_dataset2(self):
        dataset_obj = Dataset.objects.create()
        create_dataset(
            taxonset_id=1,
            geneset_id=1,
            gene_codes_ids=[],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=False,
            aminoacids=False,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        expected = ">CP100_10_Aus_aus\nACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACGACG"
        dataset_obj.refresh_from_db()
        self.assertIn(expected, dataset_obj.content)

    def test_create_dataset__aa_with_bad_codon(self):
        """Test when trying to translate 'N--' codon. Should translate to X"""
        dataset_obj = Dataset.objects.create()
        v = Vouchers.objects.get(code="CP100-10")
        seq = Sequences.objects.get(code=v, gene__gene_code="COI-begin")
        seq.sequences = "TCAN--CGTCCC"
        seq.save()

        create_dataset(
            taxonset_id=1,
            geneset_id=1,
            gene_codes_ids=[],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=False,
            aminoacids=True,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        self.assertEqual([], dataset_obj.warnings)
        self.assertEqual([], dataset_obj.errors)

    @patch('create_dataset.views.schedule_dataset')
    def test_create_dataset3(self, mock_schedule_dataset):
        mock_schedule_dataset.return_value = 1
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        res = self.c.post('/create_dataset/results/',
                          {
                              'voucher_codes': 'CP100-10',
                              'gene_codes': self.g1.id,  # COI-begin
                              'geneset': '',
                              'taxonset': '',
                              'translations': False,
                              'introns': 'YES',
                              'file_format': 'FASTA',
                              'degen_translations': 'normal',
                              'exclude': 'YES',
                              'aminoacids': False,
                              'special': False,
                              'outgroup': '',
                              'positions': 'ALL',
                              'partition_by_positions': 'by gene',
                              'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
                          },
                          )
        self.assertEqual(302, res.status_code)

    def test_results(self):
        dataset = Dataset.objects.create()
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        res = self.c.post(f'/create_dataset/results/{dataset.id}/')
        self.assertEqual(200, res.status_code)

    def test_results__not_found(self):
        self.c.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        res = self.c.post('/create_dataset/results/1/')
        self.assertEqual(404, res.status_code)
