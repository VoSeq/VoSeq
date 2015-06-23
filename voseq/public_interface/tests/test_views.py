from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.utils import override_settings

import haystack

from public_interface.views import VoSeqSearchView


# Need to use a clean index for our tests
TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'test_haystack',
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
        'INDEX_NAME': 'test_autocomplete',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
    'vouchers': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'test_vouchers',
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
        'INDEX_NAME': 'test_advanced_search',
        'INCLUDE_SPELLING': False,
        'EXCLUDED_INDEXES': [
            'public_interface.search_indexes.SimpleSearchIndex',
            'public_interface.search_indexes.VouchersIndex',
        ],
    },
}


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        # build index with our test data
        haystack.connections.reload('default')
        call_command('rebuild_index', interactive=False, verbosity=0)
        super(TestViews, self).setUp()

        self.client = Client()
        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(200, response.status_code)

    def test_browse(self):
        response = self.client.get('/browse/')
        self.assertEqual(200, response.status_code)

    def test_show_voucher(self):
        response = self.client.get('/p/CP100-10', follow=True)
        self.assertEqual(200, response.status_code)

    def test_show_voucher_doesnt_exist(self):
        response = self.client.get('/p/NN1-1aaaaaaa', follow=True)
        self.assertEqual(404, response.status_code)

    def test_show_sequence(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        response = self.client.get('/s/CP100-10/COI/')
        self.assertEqual(200, response.status_code)

    def test_show_sequence_doesnt_exist(self):
        self.client.post('/accounts/login/', {'username': 'admin', 'password': 'pass'})
        response = self.client.get('/s/NN1-1aaaaa/EF1a/')
        self.assertEqual(404, response.status_code)

    def test_search_redirected(self):
        """Get redirected to home due to empty search query
        """
        response = self.client.get('/search/?q=')
        self.assertEqual(302, response.status_code)

    def test_search_voucher_link(self):
        """Do we have correct links to voucher pages?
        """
        response = self.client.get('/search/?q=Melitaea')
        content = str(response.content)
        self.assertTrue('href="/p/CP100-14' in content)

    def test_search_hymenoptera(self):
        response = self.client.get('/search/?q=Hymenoptera')
        content = str(response.content)
        self.assertTrue('CP100-14' in content)

    def test_search_returns_empty(self):
        """Querying for several data fields should be equivalent of using AND.
        """
        # TODO rewrite this test for search/advanced
        response = self.client.get('/search/?orden=Coleoptera&code=NN1-1')
        content = str(response.content)
        self.assertFalse('NN1-2' in content and 'NN1-1' in content)

    def test_autocomplete_param_field(self):
        """Parameters field and term are required to return JSON info for
        autocomplete input boxes in advanced search GUI.
        """
        response = self.client.get('/autocomplete/?field=genus')
        self.assertEqual(404, response.status_code)

    def test_autocomplete_param_term(self):
        """Parameters field and term are required to return JSON info for
        autocomplete input boxes in advanced search GUI.
        """
        response = self.client.get('/autocomplete/?term=euptychia')
        self.assertEqual(404, response.status_code)

    def test_autocomplete(self):
        response = self.client.get('/autocomplete/?field=genus&term=melita')
        content = response.content.decode('utf-8')
        self.assertTrue('Melitaea' in content)

    def test_url_encoded_query_advanced_search1(self):
        my_view = VoSeqSearchView(url_encoded_query='page=2&genus=Melitaea', searchqueryset='')
        expected = 'genus=Melitaea'
        self.assertEqual(expected, my_view.url_encoded_query)

    def test_url_encoded_query_advanced_search2(self):
        my_view = VoSeqSearchView(url_encoded_query='&genus=Melitaea', searchqueryset='')
        expected = 'genus=Melitaea'
        self.assertEqual(expected, my_view.url_encoded_query)

    def test_url_encoded_query_simple_search1(self):
        my_view = VoSeqSearchView(url_encoded_query='q=Melitaea', searchqueryset='')
        expected = 'q=Melitaea'
        self.assertEqual(expected, my_view.url_encoded_query)

    def test_url_encoded_query_simple_search2(self):
        my_view = VoSeqSearchView(url_encoded_query='q=Melitaea&page=2', searchqueryset='')
        expected = 'q=Melitaea'
        self.assertEqual(expected, my_view.url_encoded_query)

    def test_simple_query_in_search_box(self):
        response = self.client.get('/search/advanced/?genus=melitaea')
        content = response.content.decode('utf-8')
        self.assertTrue('class="form-control" value="melitaea"' in content)

    def test_stats(self):
        call_command('create_stats')
        response = self.client.get('/search/advanced/?genus=melitaea')
        content = response.content.decode('utf-8')
        self.assertTrue('Now with 10 vouchers' in content)
