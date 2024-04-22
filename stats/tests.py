from django.test import TestCase
from django.conf import settings
from django.core.management import call_command

from public_interface.models import Vouchers, Sequences
from stats.models import Stats
from stats.models import VouchersPerGene


class TestCustomCommand(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        call_command('create_stats')

    def test_model_stats_str(self):
        res = Stats.objects.get(id=1)
        self.assertEqual("10 vouchers", str(res))

    def test_model_voucherspergene_str(self):
        res = VouchersPerGene.objects.get(gene_code="wingless")
        self.assertEqual("10 vouchers in gene wingless", str(res))

        for code in ['CP100-11', 'CP100-12', 'CP100-13', 'CP100-14', 'CP100-15',
                     'CP100-16', 'CP100-17', 'CP100-18', 'CP100-19']:
            v = Vouchers.objects.get(code=code)
            s = Sequences.objects.get(code=v, gene__gene_code="wingless")
            s.delete()
        call_command('create_stats')
        res = VouchersPerGene.objects.get(gene_code="wingless")
        self.assertEqual("1 voucher in gene wingless", str(res))

    def test_create_stats(self):
        res = Stats.objects.get(id=1)
        expected = 10
        self.assertEqual(expected, res.vouchers)

    def test_count_vouchers_per_gene(self):
        res = VouchersPerGene.objects.all().values('gene_code', 'voucher_count')
        for i in res:
            if i['gene_code'] == 'COI':
                self.assertTrue(i['voucher_count'] == 3)

            if i['gene_code'] == '16S':
                self.assertTrue(i['voucher_count'] == 1)
