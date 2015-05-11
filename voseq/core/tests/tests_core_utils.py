from django.test import TestCase
from django.core.management import call_command

from core import exceptions
from core.utils import get_gene_codes
from core.utils import get_voucher_codes
from core.utils import get_start_translation_index
from public_interface.models import TaxonSets
from public_interface.models import GeneSets
from public_interface.models import Genes


class TestGenBankFastaUtils(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        gs = GeneSets.objects.get(geneset_name='2genes')
        g = Genes.objects.get(gene_code='COI')
        g2 = Genes.objects.get(gene_code='16S')
        ts = TaxonSets.objects.get(taxonset_name='Erebia')
        self.cleaned_data = {
            'gene_codes': [g, g2],
            'taxonset': ts,
            'voucher_codes': 'CP200-10\r\n \r\nCP100-11\r\n \r\n',
            'geneset': gs,
        }

    def test_get_gene_codes(self):
        expected = 3
        result = get_gene_codes(self.cleaned_data)
        self.assertEqual(expected, len(result))

    def test_get_voucher_codes(self):
        expected = 3
        result = get_voucher_codes(self.cleaned_data)
        self.assertEqual(expected, len(result))

    def test_get_voucher_codes_order(self):
        """Voucher codes should not be sorted. Same order as input from author
        should be kept."""
        self.cleaned_data['voucher_codes'] = 'CP100-10\r\nCP100-11\r\nCP100-12\r\nCP100-13\r\nCP100-11'
        expected = ('CP100-10', 'CP100-11', 'CP100-12', 'CP100-13')
        result = get_voucher_codes(self.cleaned_data)
        self.assertEqual(expected, result)

    def test_get_voucher_codes_dropped(self):
        self.cleaned_data['voucher_codes'] = 'CP100-10\r\n--CP100-11\r\nCP100-12'
        expected = 2
        result = get_voucher_codes(self.cleaned_data)
        self.assertEqual(expected, len(result))

    def test_get_start_translation_index_case_2(self):
        removed = 10
        gene_model = {'reading_frame': 1}
        expected = 2
        result = get_start_translation_index(gene_model, removed)
        self.assertEqual(expected, result)

    def test_get_start_translation_index_case_3(self):
        removed = 11
        gene_model = {'reading_frame': 1}
        expected = 1
        result = get_start_translation_index(gene_model, removed)
        self.assertEqual(expected, result)

    def test_get_start_translation_index_case_7(self):
        removed = 9
        gene_model = {'reading_frame': 3}
        expected = 2
        result = get_start_translation_index(gene_model, removed)
        self.assertEqual(expected, result)

    def test_get_start_translation_index_case_8(self):
        removed = 10
        gene_model = {'reading_frame': 3}
        expected = 1
        result = get_start_translation_index(gene_model, removed)
        self.assertEqual(expected, result)

    def test_get_start_translation_index_case_9(self):
        removed = 11
        gene_model = {'reading_frame': 3}
        expected = 0
        result = get_start_translation_index(gene_model, removed)
        self.assertEqual(expected, result)

    def test_get_start_translation_index_missing_reading_frame(self):
        removed = 11
        gene_model = {'reading_frame': 1, 'gene_code': 'test_gene'}
        self.assertRaises(exceptions.MissingReadingFrameForGene,
                          get_start_translation_index, gene_model, removed)
