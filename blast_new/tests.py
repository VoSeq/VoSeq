from django.conf import settings
from django.test import TestCase, Client
from django.core.management import call_command


class TestBlastNew(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()

    def test_index(self):
        response = self.client.get('/blast_new/', follow=True)
        self.assertEqual(200, response.status_code)

    def test_result(self):
        response = self.client.post('/blast_new/results/', {
            'name': 'aaaa',
            'sequence': 'ATCGATCGGCTA',
            'gene_codes': ['COI'],
        }, follow=True)
        self.assertEqual(200, response.status_code)

    def test_result_more_than_one_gene(self):
        response = self.client.post('/blast_new/results/', {
            'name': 'aaaa',
            'sequence': 'ATCGATCGGCTA',
            'gene_codes': ['COI', 'wingless'],
        }, follow=True)
        self.assertEqual(200, response.status_code)

    def test_result_no_gene_code_given(self):
        response = self.client.post('/blast_new/results/', {
            'name': 'aaaa',
            'sequence': 'ATCGATCGGCTA',
            'gene_codes': [],
        }, follow=True)
        self.assertEqual(200, response.status_code)

    def test_result_invalid_form(self):
        response = self.client.post('/blast_new/results/', {
            'name': 'aaaa',
            'sequence': '123GATCGGCTA',
            'gene_codes': ['COI'],
        }, follow=True)
        self.assertEqual(200, response.status_code)

    def test_redirect(self):
        response = self.client.get('/blast_new/results/')
        self.assertEqual(302, response.status_code)
