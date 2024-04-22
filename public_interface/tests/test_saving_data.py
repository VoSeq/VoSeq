from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

from public_interface.models import Sequences
from public_interface.models import Vouchers


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.voucher_model = Vouchers.objects.get(code='CP100-18')
        self.maxDiff = None

    def test_save_sequences_ambiguous_characters(self):
        sequence_model = Sequences.objects.get(
            code=self.voucher_model,
            gene__gene_code='COI',
        )
        sequence_model.sequences = '???---NNNATCTACTA'
        sequence_model.save()

        sequence_model = Sequences.objects.get(
            code=self.voucher_model,
            gene__gene_code='COI',
        )
        self.assertEqual(sequence_model.number_ambiguous_bp, 9)
