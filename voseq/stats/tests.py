from django.test import TestCase
from django.core.management import call_command

from stats.models import Stats
from stats.models import VouchersPerGene


class TestCustomCommand(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_create_stats(self):
        call_command('create_stats')
        res = Stats.objects.get(id=1)
        expected = 10
        self.assertEqual(expected, res.vouchers)

    def test_count_vouchers_per_gene(self):
        call_command('create_stats')
        res = VouchersPerGene.objects.all().values('gene_code', 'voucher_count')
        for i in res:
            if i['gene_code'] == 'COI':
                self.assertTrue(i['voucher_count'] == 3)

            if i['gene_code'] == '16S':
                self.assertTrue(i['voucher_count'] == 1)
