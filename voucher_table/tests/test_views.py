from django.core.management import call_command
from django.conf import settings
from django.db import connection
from django.test import Client, TestCase


class TestViews(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("alter sequence public_interface_taxonsets_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_genesets_id_seq restart with 1")
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()
        self.maxDiff = None

    def test_index(self):
        response = self.client.get('/create_voucher_table/', follow=True)
        self.assertEqual(200, response.status_code)

    def test_result_redirect(self):
        response = self.client.get('/create_voucher_table/results/')
        self.assertEqual(302, response.status_code)

    def test_results(self):
        expected = 'CP100-10,669,1227,412'
        response = self.client.post('/create_voucher_table/results/',
                                    {
                                        'voucher_info': 'code',
                                        'voucher_codes': '',
                                        'taxonset': 1,
                                        'geneset': 1,
                                    },
                                    follow=True,
                                    )
        self.assertTrue(expected in response.content.decode('utf-8'))
