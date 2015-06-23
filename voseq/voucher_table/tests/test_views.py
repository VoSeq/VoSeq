from django.test import Client
from django.test import TestCase
from django.core.management import call_command


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()
        self.maxDiff = None

    def test_index(self):
        response = self.client.get('/create_voucher_table/')
        self.assertEqual(200, response.status_code)

    def test_result_redirect(self):
        response = self.client.get('/create_voucher_table/results/')
        self.assertEqual(302, response.status_code)

    def test_results(self):
        expected = 'CP100-10,515,669'
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
