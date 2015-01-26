from django.test import TestCase
from django.core.management import call_command

from public_interface.models import GeneSets
from public_interface.models import Genes
from genbank_fasta import utils


class TestGenBankFastaUtils(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        gs = GeneSets.objects.get(geneset_name='4genes')
        g = Genes.objects.get(gene_code='COI')
        self.cleaned_data = {
            'gene_codes': [g],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': gs,
        }

    def test_get_gene_codes(self):
        expected = 4
        result = utils.get_gene_codes(self.cleaned_data)
        self.assertEqual(expected, len(result))

    def test_dataset_reading_frame_2(self):
        res = utils.Results(['CP100-10', 'CP100-11'], ['COI'])
        res.get_datasets()
        self.assertEqual('WAGMIGTSLSLIIRTELGNP', res.protein.splitlines()[1][0:20])
