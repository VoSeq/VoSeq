from django.test import TestCase
from django.core.management import call_command
from django.test import Client


class TestGeneTable(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        self.client = Client()

    def test_view_index(self):
        response = self.client.get('/create_gene_table/')
        self.assertEqual(200, response.status_code)

    def test_results(self):
        expected = 'COI,mitochondrial,1047,58.357,42.0,0.0,58.0,17.299999999999997,22.5,9.5,9.1'
        response = self.client.post('/create_gene_table/results/',
                                    {
                                        'taxonset': 1,
                                        'geneset': 1,

                                    })
        self.assertTrue(expected in str(response.content))

    def test_results_invalid_form(self):
        response = self.client.post('/create_gene_table/results/', {
            'taxonset': 1000,
            'geneset': 1000,
        })
        expected = 'Erebia'
        self.assertTrue(expected in str(response.content))
