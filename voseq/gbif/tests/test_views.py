from django.core.management import call_command
from django.test import TestCase
from django.test import Client


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()

    def test_index(self):
        response = self.client.get('/share_data_gbif/')
        self.assertEqual(200, response.status_code)

    def test_dump_data_error(self):
        response = self.client.get('/share_data_gbif/dump_data/')
        result = response.content.decode('utf-8')
        expected = '{"result": "error"}'
        self.assertEqual(expected, result)

    def test_dump_data_count_data(self):
        response = self.client.get('/share_data_gbif/dump_data/',
                                   {'request': 'count_data'})
        result = response.content.decode('utf-8')
        expected = '"count": 10'
        self.assertTrue(expected in result)

    def test_dump_data_make_file(self):
        response = self.client.get('/share_data_gbif/dump_data/',
                                   {'request': 'make_file'})
        result = response.content.decode('utf-8')
        expected = 'CP100-15,,,Nymphalidae,,Melitaeini,Melitaeina'
        self.assertTrue(expected in result)
