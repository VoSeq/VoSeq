from django.core.management import call_command
from django.test import TestCase

from public_interface.models import Sequences
from public_interface.models import Vouchers


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_save_sequences_ambiguous_characters(self):
        voucher_model = Vouchers.objects.get(code='CP100-18')
        sequence_model = Sequences(
            code=voucher_model,
            sequences='???---NNNATCTACTA',
            gene_code='COI',
            genbank=False,
        )
        sequence_model.save()

        sequence_model = Sequences.objects.get(code=voucher_model, gene_code='COI')
        self.assertEqual(sequence_model.number_ambiguous_bp, 9)
