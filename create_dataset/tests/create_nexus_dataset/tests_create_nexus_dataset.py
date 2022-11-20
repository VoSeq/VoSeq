import os

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from create_dataset.utils import CreateDataset
from public_interface.models import Genes
from public_interface.models import GeneSets
from public_interface.models import TaxonSets


class CreateNexusDatasetTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        gene_set = GeneSets.objects.get(geneset_name='all_genes')
        taxon_set = TaxonSets.objects.get(taxonset_name='all_taxa')
        self.cleaned_data = {
            'gene_codes': '',
            'taxonset': taxon_set,
            'voucher_codes': '',
            'geneset': gene_set,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'translations': False,
            'degen_translations': 'normal',
            'number_genes': None,
            'positions': ['ALL'],
            'partition_by_positions': 'by gene',
            'file_format': 'NEXUS',
            'aminoacids': False,
            'outgroup': None,
        }

        Genes.objects.all().update(genetic_code=1)

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_nexus_all_codons_as_one(self):
        dataset_file = os.path.join(self.base_dir, 'create_nexus_dataset', 'dataset.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['ALL']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_all_codons_partitioned_as_each(self):
        dataset_file = os.path.join(
            self.base_dir, 'create_nexus_dataset', 'dataset_partitioned_as_each.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['ALL']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_all_codons_partitioned_as_1st2nd_3rd(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_partitioned_as_1st2nd_3rd.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['ALL']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_codon_as_one(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_codon_as_each(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_codon_as_1st2nd_3rd(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_2nd_codon_as_one(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_2nd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_2nd_codon_as_each(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_2nd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_2nd_codon_as_1st2nd_3rd(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_2nd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_3rd_codon_as_one(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_3rd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['3rd']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_3rd_codon_as_each(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_3rd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['3rd']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_3rd_codon_as_1st2nd_3rd(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_3rd_codon.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['3rd']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_2nd_codon_as_one(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st2nd_codons.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_2nd_codon_as_each(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st2nd_codons_partitioned_as_each.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_2nd_codon_as_1st2nd_3rd(self):
        dataset_file = os.path.join(self.base_dir,
                                    'create_nexus_dataset', 'dataset_1st2nd_codons_partitioned_as_1st2nd_3rd.nex')
        with open(dataset_file, 'r') as handle:
            expected = handle.read()

        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        result = dataset_creator.dataset_str
        self.assertEqual(expected.strip(), result)

    def test_nexus_1st_3rd_codon_as_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '3rd']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_1st_3rd_codon_as_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '3rd']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_1st_3rd_codon_as_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['1st', '3rd']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'Cannot create dataset for only codon positions 1st and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_2nd_3rd_codon_as_one(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd', '3rd']
        cleaned_data['partition_by_positions'] = 'by gene'
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_2nd_3rd_codon_as_each(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd', '3rd']
        cleaned_data['partition_by_positions'] = 'by codon position'
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_2nd_3rd_codon_as_1st2nd_3rd(self):
        cleaned_data = self.cleaned_data.copy()
        cleaned_data['positions'] = ['2nd', '3rd']
        cleaned_data['partition_by_positions'] = '1st-2nd, 3rd'
        dataset_creator = CreateDataset(cleaned_data)

        expected = 'Cannot create dataset for only codon positions 2nd and 3rd.'
        result = dataset_creator.errors
        self.assertTrue(expected in ''.join([str(i) for i in result]))

    def test_nexus_with_outgroup(self):
        cleaned_data = self.cleaned_data
        cleaned_data['outgroup'] = 'CP100-11'
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='all_genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = "outgroup CP100_11_Aus_bus;"
        self.assertTrue(expected in result)

    def test_nexus_gene_no_reading_frame(self):
        # For this test we will set the reading frame of ArgKin to None
        argkin = Genes.objects.get(gene_code='ArgKin')
        argkin.reading_frame = None
        argkin.save()

        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='all_genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        self.assertEqual('', result)
        self.assertEqual('reading_frame attribute for gene ArgKin should be either '
                         '1, 2 or 3.', str(dataset_creator.errors[0]))

    """
    def test_nexus_gene_excluding_taxa(self):
        # Voucher CP100-11 should be dropped
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['1st', '2nd']
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='all_genes')
        cleaned_data['number_genes'] = 4
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = ""
        self.assertEqual(expected.strip(), result)
    """

    def test_with_total_char_lengths_aminoacids(self):
        cleaned_data = self.cleaned_data
        cleaned_data['aminoacids'] = True
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='all_genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
#NEXUS

BEGIN DATA;
DIMENSIONS NTAX=10 NCHAR=1575;
"""
        self.assertTrue(expected.strip() in result)

    def test_char_lengths_for_partitions_aminoacids(self):
        cleaned_data = self.cleaned_data
        cleaned_data['aminoacids'] = True
        cleaned_data['outgroup'] = ''
        cleaned_data['geneset'] = GeneSets.objects.get(geneset_name='all_genes')
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = "charset ef1a = 689-1101"
        self.assertTrue(expected in result)

    def test_order_of_vouchers_is_kept_along_partitions(self):
        cleaned_data = self.cleaned_data
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = """
CP100_19_Aus_jus                                       ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

[ef1a]
"""
        self.assertTrue(expected.strip() in result)

    def test_try_dataset_degenerated_in_partitions(self):
        cleaned_data = self.cleaned_data
        cleaned_data['voucher_codes'] = 'CP100-10'
        cleaned_data['degen_translations'] = 'normal'
        cleaned_data['partition_by_positions'] = 'by gene'
        cleaned_data['translations'] = True
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = "DIMENSIONS NTAX=10 NCHAR=4732;"
        self.assertTrue(expected in result)
