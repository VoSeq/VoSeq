from django.core.management import call_command
from django.test import Client
from django.test import TestCase


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        call_command('create_stats')

        self.client = Client()

    def test_genes(self):
        response = self.client.get('/genes/')
        self.assertEqual(200, response.status_code)

    def test_genes_with_number_of_vouchers(self):
        response = self.client.get('/genes/')
        expected = '3 vouchers'
        result = str(response.content)
        self.assertTrue(expected in result)

    def test_view_gene(self):
        response = self.client.get('/genes/wingless/')
        self.assertEqual(200, response.status_code)

    def test_view_gene_not_found(self):
        response = self.client.get('/genes/winglessaaaaaa/')
        self.assertEqual(200, response.status_code)
