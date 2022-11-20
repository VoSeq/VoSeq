import os

from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth.models import User

from create_dataset.utils import CreateDataset
from public_interface.models import GeneSets, Genes
from public_interface.models import Sequences
from public_interface.models import TaxonSets
from public_interface.models import Vouchers


class CreatePhylipDatasetTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        Genes.objects.all().update(genetic_code=1)

        gene_set = GeneSets.objects.get(geneset_name='all_genes')
        taxon_set = TaxonSets.objects.get(taxonset_name='all_taxa')
        self.cleaned_data = {
            'gene_codes': '',
            'taxonset': taxon_set,
            'voucher_codes': '',
            'geneset': gene_set,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'number_genes': None,
            'degen_translations': None,
            'positions': ['ALL'],
            'translations': False,
            'partition_by_positions': 'by gene',
            'file_format': 'PHYLIP',
            'aminoacids': False,
            'outgroup': '',
        }
        self.dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                         'tests', 'create_phylip_dataset', 'dataset.phy')
        self.aa_dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                            'tests', 'create_phylip_dataset', 'aa_dataset.phy')

        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_create_simple_dataset(self):
        with open(self.dataset_file, "r") as handle:
            expected = handle.read()
        result = self.dataset_creator.dataset_str
        self.assertEqual(expected, result)

    def test_charset_block_file_of_simple_dataset(self):
        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        result = self.dataset_creator.charset_block
        self.assertEqual(expected, result)

    def test_create_aa_dataset(self):
        with open(self.aa_dataset_file, "r") as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected, result)

    def test_create_aa_dataset_charset_block(self):
        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_aa_file.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.charset_block
        self.assertEqual(expected, result)

    def test_stop_codon_warning(self):
        voucher = Vouchers.objects.get(code='CP100-10')
        sequence_with_stop_codon = 'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNtaaTCTGTAGGCGATGCCTTGAAGGACGGCTTCGACGGAGCGTCGCGGGTCATGATGCCCAATACGGAGTTAGAAGCGCCTGCTCAGCGAAACGACGCCGCCCCGCACAGAGTCCCGCGACGAGACCGATACAGATTTCAACTTCGGCCGCACAATCCTGACCACAAAACACCCGGANTCAAGGACCTAGTGTACTTGGAATCATCGCCGGGTTTCTGCGAAAAGAACCCGCGGCTGGGCATTCCCGGCACGCACGGGCGTGCCTGCAACGACACGAGTATCGGCGTCGACGGCTGCGACCTCATGTGCTGCGGCCGTGGCTACCGGACCGAGACAATGTTCGTCGTGGAGCGATGCAAC'
        seq = Sequences.objects.get(code=voucher, gene__gene_code='wingless')
        seq.sequences = sequence_with_stop_codon
        seq.save()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)

        expected = "Gene wingless, sequence CP100_10 contains stop codons '*'"
        result = dataset_creator.warnings
        self.assertEqual(expected, result[0])

    def test_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        expected = "CP100_10_Aus_aus  ACGACGACGA CGACGACGAC GACGACGACG ACGACGACGA CGACGACGAC"
        self.assertTrue(expected in result)

    def test_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        expected = "CP100_10_Aus_aus  ACGACGACGA CGACGACGAC GACGACGACG ACGACGACGA CGACGACGAC"
        self.assertTrue(expected in result)

    def test_dataset_1st_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_1st_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_1st_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_1st_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_partitioned_1st2nd_3rd.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_partitioned_1st_2nd_3rd.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_2nd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_2nd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_2nd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_2nd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_2nd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_2nd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_2nd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_2nd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_2nd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_2nd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_2nd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_2nd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_3rd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_3rd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_3rd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_3rd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_3rd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_3rd_codon.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_3rd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_3rd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_3rd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_3rd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_3rd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['3rd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset', 'charset_block_file_dataset_3rd_codon.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st2nd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st2nd_codons.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st2nd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st2nd_codons.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st2nd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str

        dataset_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                    'tests', 'create_phylip_dataset', 'dataset_1st2nd_codons.phy')
        with open(dataset_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st2nd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset',
                                          'charset_block_dataset_1st2nd_codons_partitioned_one.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st2nd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset',
                                          'charset_block_dataset_1st2nd_codons_partitioned_each.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_charset_block_dataset_1st2nd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['1st', '2nd']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.charset_block

        charset_block_file = os.path.join(settings.BASE_DIR, '..', 'create_dataset',
                                          'tests', 'create_phylip_dataset',
                                          'charset_block_dataset_1st2nd_codons_partitioned_1st2nd_3rd.txt')
        with open(charset_block_file, "r") as handle:
            expected = handle.read()
        self.assertEqual(expected, result)

    def test_dataset_1st3rd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['1st', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))

    def test_dataset_1st3rd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['1st', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))

    def test_dataset_1st3rd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        cleaned_data['positions'] = ['1st', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))

    def test_dataset_2nd3rd_codon_partitioned_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['positions'] = ['2nd', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))

    def test_dataset_2nd3rd_codon_partitioned_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = 'by codon position'
        cleaned_data['positions'] = ['2nd', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))

    def test_dataset_2nd3rd_codon_partitioned_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['partition_by_positions'] = '1st-2nd,3rd'
        cleaned_data['positions'] = ['2nd', '3rd']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors[0]
        self.assertEqual(expected, str(result))
