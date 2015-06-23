import re

from django.test import TestCase
from django.test import Client
from django.core.management import call_command
from django.contrib.auth.models import User


class TestGenBankFasta(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()
        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

    def test_index(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.get('/genbank_fasta/')
        self.assertEqual(200, c.status_code)

    def test_results(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': 'CP100-10\r\nCP100-11',
                                 'gene_codes': [],
                                 'geneset': '4genes',
                                 'taxonset': None,
                             }
                             )
        self.assertEqual(200, c.status_code)

    def test_results_dataset(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': 'CP100-10',
                                 'gene_codes': 4,  # COI is in 4th position in our GUI gene list
                                 'geneset': '',
                                 'taxonset': '',
                             }
                             )
        expected = "organism=Melitaea diamina"
        self.assertTrue(expected.strip() in str(c.content))
        expected = "TGAGCCGGTATAATTGGTACATCCCTAAGTCTTATTATTCGAACCGAATTAGGAAATCCTAGTTTTTTAATTGGAGATGATCAAATTTATAATACCATTGTAACAGCTCATGCTTTTATTATAATTTTTTTTATAGTTATGCCAATTATAATTGGAGGATTTGGTAATTGACTTGTACCATTAATATTGGGAGCCCCAGATATAGCTTTCCCCCGAATAAATTATATAAGATTTTGATTATTGCCTCCATCCTTAATTCTTTTAATTTCAAGTAGAATTGTAGAAAATGGGGCAGGAACTGGATGAACAGTTTACCCCCCACTTTCATCTAATATTGCCCATAGAGGAGCTTCAGTGGATTTAGCTATTTTTTCTTTACATTTAGCTGGGATTTCCTCTATCTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAATTAATAATATATCTTATGATCAAATACCTTTATTTGTATGAGCAGTAGGAATTACAGCATTACTTCTCTTATTATCTTTACCAGTTTTAGCTGGAGCTATTACTATACTTTTAACGGATCGAAATCTTAATACCTCATTTTTTGATTCCTGCGGAGGAGGAGATCC"
        self.assertTrue(expected.strip() in str(c.content))

    def test_results_valid_form(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': None,
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': 1,
                             }
                             )
        self.assertEqual(200, c.status_code)

    def test_results_valid_form_no_taxon(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': '',
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': None,
                             }
                             )
        self.assertEqual(200, c.status_code)

    def test_results_fasta_file(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        c = self.client.post('/genbank_fasta/results/',
                             {
                                 'voucher_codes': None,
                                 'gene_codes': [],
                                 'geneset': 1,
                                 'taxonset': 1,
                             }
                             )
        res = re.search('(GenbankFASTA_[0-9a-z]+\.txt)', str(c.content))
        fasta_filename = res.groups()[0]
        d = self.client.get('/genbank_fasta/results/' + fasta_filename + '/')
        self.assertEqual(200, d.status_code)

    def test_results_get(self):
        c = self.client.get('/genbank_fasta/results/')
        self.assertEqual(302, c.status_code)
