from django.test import TestCase, Client
from django.conf import settings
from django.core.management import call_command

from overview_table.utils import OverviewTableMaker


class TestOverviewTable(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        call_command('create_stats')

    def test_utils(self):
        o = OverviewTableMaker()
        expected = 6
        result = len(o.items)
        self.assertEqual(expected, result)


class TestViews(TestCase):
    def test_index_view(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        call_command('create_stats')

        c = Client()
        response = c.get('/view_table/', follow=True)
        self.assertEqual(200, response.status_code)
