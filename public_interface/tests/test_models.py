from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from public_interface.models import Sequences
from public_interface.models import Vouchers


class TestModels(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_voucher_str(self):
        voucher_model = Vouchers.objects.get(code='CP100-18')
        expected = 'CP100-18 Melitaea diamina'
        self.assertEqual(expected, voucher_model.__str__())

    def test_sequences_str(self):
        voucher_model = Vouchers.objects.get(code='CP100-10')
        sequences_model = Sequences.objects.get(code=voucher_model, gene__gene_code='COI')
        expected = 'sequence'
        self.assertEqual(expected, sequences_model.__str__())
