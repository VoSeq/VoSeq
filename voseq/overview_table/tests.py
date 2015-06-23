from django.test import TestCase
from django.core.management import call_command
from django.test import Client

from overview_table.utils import OverviewTableMaker


class TestOverviewTable(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        call_command('create_stats')

    def test_utils(self):
        o = OverviewTableMaker()
        expected = 3
        result = len(o.items)
        self.assertEqual(expected, result)


class TestViews(TestCase):
    def test_index_view(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)
        call_command('create_stats')

        c = Client()
        response = c.get('/view_table/')
        self.assertEqual(200, response.status_code)
