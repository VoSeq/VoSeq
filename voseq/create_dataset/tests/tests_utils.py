from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from create_dataset.utils import CreateDataset
from public_interface.models import Genes


class CreateDatasetUtilsTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        g1 = Genes.objects.get(gene_code='COI')
        g2 = Genes.objects.get(gene_code='EF1a')
        self.cleaned_data = {
            'gene_codes': [g1, g2],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': None,
            'taxon_names': ['CODE', 'SUPERFAMILY', 'GENUS', 'SPECIES']
        }

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)

    def test_create_dataset(self):
        expected = '>CP100-10_Papilionoidea_Melitaea_diamina'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_get_taxon_names_for_taxa(self):
        expected = {
            'cp100-10': {'code': 'CP100-10', 'genus': 'Melitaea', 'species': 'diamina', 'superfamily': 'Papilionoidea'},
            'cp100-11': {'code': 'CP100-11', 'genus': 'Melitaea', 'species': 'diamina', 'superfamily': ''},
        }
        result = self.dataset_creator.get_taxon_names_for_taxa()

        self.assertEqual(expected, result)

    def test_get_taxon_names_for_taxa_additional_fields(self):
        self.cleaned_data['taxon_names'] = ['SUPERFAMILY']
        dataset_creator = CreateDataset(self.cleaned_data)
        expected = {
            'cp100-10': {'superfamily': 'Papilionoidea'},
            'cp100-11': {'superfamily': ''},
        }
        result = dataset_creator.get_taxon_names_for_taxa()

        self.assertEqual(expected, result)
