from django.test import TestCase
from django.core.management import call_command

from public_interface.models import GeneSets
from public_interface.models import TaxonSets
from voucher_table.views import VoucherTable


class TestVoucherTable(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        taxonset = TaxonSets.objects.all()[0]
        geneset = GeneSets.objects.all()[0]

        self.cleaned_data = {
            'collector_info': ['country', 'specificLocality', 'collector'],
            'gene_codes': [],
            'gene_info': 'NUMBER OF BASES',
            'voucher_info': ['code', 'genus', 'species'],
            'field_delimitor': 'COMMA',
            'taxonset': taxonset,
            'voucher_codes': '',
            'geneset': geneset,
        }
        self.table = VoucherTable(self.cleaned_data)

    def test_header_csv_file(self):
        expected = ('Code', 'Genus', 'Species', 'Country', 'Specific Locality', 'Collector', '16S',
                    'COI', 'EF1a', 'wingless')
        result = self.table.get_headers()
        self.assertEqual(expected, result)

    def test_create_csv_file_taxa(self):
        expected = 'CP100-10,Melitaea,diamina'
        response = self.table.create_csv_file()
        result = response.content
        self.assertTrue(expected in result.decode('utf-8'))

    def test_create_csv_file_genes(self):
        expected = '515,669,1227,412'
        response = self.table.create_csv_file()
        result = response.content.decode('utf-8')
        self.assertTrue(expected in result)

    def test_create_csv_missing_voucher(self):
        cleaned_data = self.cleaned_data
        cleaned_data['voucher_codes'] = 'CP1000-1000'
        table = VoucherTable(cleaned_data)
        table.create_csv_file()
        expected = 'We don\'t have voucher CP1000-1000 in our database.'
        result = table.warnings
        self.assertTrue(expected in result)

    def test_create_csv_missing_sequence(self):
        expected = 'We don\'t have sequences for 16S and CP100-11'
        self.table.create_csv_file()
        result = self.table.warnings
        self.assertTrue(expected in result)
