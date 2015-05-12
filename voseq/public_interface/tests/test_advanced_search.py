from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from django.test.utils import override_settings
import haystack


# Need to use a clean index for our tests
TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
        'INCLUDE_SPELLING': True,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.AdvancedSearchIndex',
            'public_interface.search_indexes.AutoCompleteIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'autocomplete': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'autocomplete',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'vouchers': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'vouchers',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.AdvancedSearchIndex',
            'public_interface.search_indexes.AutoCompleteIndex',
        ],
    },
    'advanced_search': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'advanced_search',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class TestAdvancedSearch(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        # build index with our test data
        haystack.connections.reload('default')
        call_command('rebuild_index', interactive=False, verbosity=0)
        super(TestAdvancedSearch, self).setUp()

        self.client = Client()

    def test_advanced_search_invalid(self):
        response = self.client.get('/search/advanced/?latitude=Hola')
        content = response.content.decode('utf-8')
        self.assertTrue('No results found.' in content)

    def test_advanced_search_gui_form(self):
        response = self.client.get('/search/advanced/')
        content = response.content.decode('utf-8')
        self.assertTrue('Search by querying a single field for any combination of fields' in content)

    def test_advanced_search_voucher_objs(self):
        response = self.client.get('/search/advanced/?orden=Hymenoptera')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_advanced_search_sequence_objs(self):
        response = self.client.get('/search/advanced/?labPerson=Niklas')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_advanced_search_dont_show_duplicate_records(self):
        """Since we are looking into the Sequences tables, we might get
        several sequences belonging to the same voucher. Need to get only
        one.
        """
        response = self.client.get('/search/advanced/?labPerson=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertEqual(1, content.count('/p/CP100-10'))

    def test_advanced_search_dont_show_duplicate_records2(self):
        response = self.client.get('/search/advanced/?labPerson=Fulano+Sutano')
        content = response.content.decode('utf-8')
        self.assertEqual(0, content.count('/p/CP100-10'))

    def test_advanced_search_sequence_table_only(self):
        response = self.client.get('/search/advanced/?labPerson=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-10' in content)
        self.assertTrue('/p/CP100-11' in content)

    def test_advanced_search_voucher_table_only(self):
        response = self.client.get('/search/advanced/?orden=Lepidoptera')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-11' in content)
        self.assertTrue('/p/CP100-13' in content)
        self.assertFalse('/p/CP100-10' in content)

    def test_advanced_search_combined(self):
        response = self.client.get('/search/advanced/?orden=Lepidoptera&labPerson=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('/p/CP100-11' in content)
        self.assertFalse('/p/CP100-10' in content)
        self.assertFalse('/p/CP100-13' in content)

    def test_advanced_search_no_result(self):
        response = self.client.get('/search/advanced/?orden=Coleoptera&labPerson=Niklas+Wahlberg')
        content = response.content.decode('utf-8')
        self.assertTrue('No results found' in content)

    def test_advanced_search_by_accession(self):
        response = self.client.get('/search/advanced/?accession=AY218260')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_genbank_true(self):
        response = self.client.get('/search/advanced/?genbank=y')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)

    def test_advanced_search_genbank_false(self):
        response = self.client.get('/search/advanced/?genbank=n')
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-15' in content)

    def test_advanced_search_by_gene_code(self):
        response = self.client.get('/search/advanced/?gene_code=1')  # gene 16S
        content = response.content.decode('utf-8')
        self.assertTrue('CP100-10' in content)
