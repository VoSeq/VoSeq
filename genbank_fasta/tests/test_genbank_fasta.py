import re
from unittest import skip

from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase, Client
from django.conf import settings


class TestGenBankFasta(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("alter sequence public_interface_genes_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_genesets_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_taxonsets_id_seq restart with 1")
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()
        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()
        self.maxDiff = None

    def test_index(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.get('/genbank_fasta/', follow=True)
        self.assertEqual(200, c.status_code)

    def test_results(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': 'CP100-10\r\nCP100-11',
                                 'gene_codes': [],
                                 'geneset': '4genes',
                                 'taxonset': '',
                             }
                             )
        self.assertEqual(200, c.status_code)

    @skip('fix tests to reflect workflow when using celery')
    def test_results_dataset(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post(
            '/genbank_fasta/results/',
         {
                 'voucher_codes': 'CP100-10',
                 'gene_codes': 4,  # COI is in 4th position in our GUI gene list
                 'geneset': '',
                 'taxonset': '',
             },
            follow=True
        )
        expected = "org=Melitaea diamina"
        self.assertTrue(expected in str(c.content))
        expected = "?????????????????????????TGAGCCGGTATAATTGGTACA"
        self.assertTrue(expected in str(c.content))

    @skip('fix tests to reflect workflow when using celery')
    def test_results_valid_form(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': '',
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': 1,
                             }, follow=True
                             )
        self.assertEqual(200, c.status_code)

    def test_results_valid_form_no_taxon(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': '',
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': '',
                             }
                             )
        self.assertEqual(200, c.status_code)

    @skip('fix tests to reflect workflow when using celery')
    def test_results_fasta_file(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': '',
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': 1,
                             }
                             )
        res = re.search('(GenBankFASTA_[0-9a-z]+\.txt)', str(c.content))
        fasta_filename = res.groups()[0]
        d = self.client.get('/genbank_fasta/results/' + fasta_filename + '/')
        self.assertEqual(200, d.status_code)

    def test_results_get(self):
        c = self.client.get('/genbank_fasta/results/')
        self.assertEqual(302, c.status_code)
