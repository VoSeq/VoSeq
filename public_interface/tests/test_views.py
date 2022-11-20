from unittest import skip

from django.core.management import call_command
from django.test import Client
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from public_interface.utils import VoSeqSearchView


class TestViews(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        super(TestViews, self).setUp()

        self.client = Client()
        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

    def test_index(self):
        response = self.client.get('/', follow=True)
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

    @skip
    def test_autocomplete_param_field(self):
        """Parameters field and term are required to return JSON info for
        autocomplete input boxes in advanced search GUI.
        """
        response = self.client.get('/autocomplete/?field=genus')
        self.assertEqual(404, response.status_code)

    @skip
    def test_autocomplete_param_term(self):
        """Parameters field and term are required to return JSON info for
        autocomplete input boxes in advanced search GUI.
        """
        response = self.client.get('/autocomplete/?term=euptychia')
        self.assertEqual(404, response.status_code)

    @skip
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
