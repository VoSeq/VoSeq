from django.core.management import call_command
from django.db import connection
from django.test import Client, TestCase
from django.conf import settings


class TestAdvancedSearch(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("alter sequence public_interface_genes_id_seq restart with 1")
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.client = Client()

    def test_advanced_search_combined(self):
        response = self.client.get('/search/advanced/?orden=Lepidoptera&lab_person=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-11' in content)
        self.assertFalse('/p/CP100-10' in content)
        self.assertFalse('/p/CP100-13' in content)

    def test_advanced_search_dont_show_duplicate_records(self):
        """Since we are looking into the Sequences tables, we might get
        several sequences belonging to the same voucher. Need to get only
        one.
        """
        response = self.client.get('/search/advanced/?lab_person=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertEqual(1, content.count('/p/CP100-10'))

    def test_advanced_search_dont_show_duplicate_records2(self):
        response = self.client.get('/search/advanced/?lab_person=Fulano+Sutano')
        content = response.content.decode('utf-8')
        self.assertEqual(0, content.count('/p/CP100-10'))

    def test_advanced_search_genbank_true(self):
        response = self.client.get('/search/advanced/?genbank=y')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_genbank_false(self):
        response = self.client.get('/search/advanced/?genbank=n')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-15' in content)

    def test_advanced_search_gui_form(self):
        response = self.client.get('/search/advanced/')
        content = response.content.decode('utf-8')
        self.assertTrue('Search by querying a single field for any combination of fields' in content)

    def test_advanced_search_invalid(self):
        response = self.client.get('/search/advanced/?latitude=Hola')
        content = response.content.decode('utf-8')
        self.assertTrue('Enter a number.' in content)

    def test_advanced_search_no_result(self):
        response = self.client.get('/search/advanced/?orden=Coleoptera&lab_person=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('No results found' in content)

    def test_advanced_search_sequence_objs(self):
        response = self.client.get('/search/advanced/?lab_person=Niklas')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_advanced_search_sequence_table_only(self):
        response = self.client.get('/search/advanced/?lab_person=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-10' in content)
        self.assertTrue('/p/CP100-11' in content)

    def test_advanced_search_sequence_table_only_check_genus(self):
        response = self.client.get('/search/advanced/?lab_person=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_advanced_search_voucher_objs(self):
        response = self.client.get('/search/advanced/?orden=Hymenoptera')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_advanced_search_voucher_table_only(self):
        response = self.client.get('/search/advanced/?orden=Lepidoptera')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-11' in content)
        self.assertTrue('/p/CP100-13' in content)
        self.assertFalse('/p/CP100-10' in content)

    def test_advanced_search_by_accession(self):
        response = self.client.get('/search/advanced/?accession=AY218260')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_by_author(self):
        response = self.client.get('/search/advanced/?author=auctorum')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-17' in content)

    def test_advanced_search_by_code_bold(self):
        response = self.client.get('/search/advanced/?code_bold=BCIBT193-09')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-18' in content)

    def test_advanced_search_by_collector(self):
        response = self.client.get('/search/advanced/?collector=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-16' in content)

    def test_advanced_search_by_country(self):
        response = self.client.get('/search/advanced/?country=FINLAND')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_date_collection(self):
        response = self.client.get('/search/advanced/?date_collection=1996-03-25')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_extraction_tube(self):
        response = self.client.get('/search/advanced/?extraction_tube=09')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_gene_code(self):
        response = self.client.get('/search/advanced/?gene_code=1')  # gene 16S
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_by_hostorg(self):
        response = self.client.get('/search/advanced/?hostorg=hostorg')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-16' in content)

    def test_advanced_search_by_type_species_negative(self):
        response = self.client.get('/search/advanced/?type_species=yes&code=CP100-09')
        content = response.content.decode('utf-8')
        self.assertTrue('No results found' in content)

    def test_advanced_search_by_type_species_unknown(self):
        response = self.client.get('/search/advanced/?type_species=unknown')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_type_species_positive(self):
        response = self.client.get('/search/advanced/?type_species=yes')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_by_sex(self):
        response = self.client.get('/search/advanced/?sex=female')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_specific_locality(self):
        response = self.client.get('/search/advanced/?specific_locality=Orivesi')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-09' in content)

    def test_advanced_search_by_voucher_locality(self):
        response = self.client.get('/search/advanced/?voucher_locality=NSG coll')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-16' in content)
