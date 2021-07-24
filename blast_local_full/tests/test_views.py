from django.test import TestCase, Client
from django.core.management import call_command
from django.conf import settings


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()

        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_index(self):
        response = self.client.get('/blast_local_full/CP100-10/COI/', follow=True)
        self.assertEqual(200, response.status_code)
