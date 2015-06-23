from django.core.management import call_command
from django.test import TestCase

from gbif.utils import get_type_species
from gbif.utils import get_sex
from gbif.utils import get_voucher_state


class TestUtils(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_get_type_species_other_text(self):
        result = get_type_species('dummy value')
        expected = ''
        self.assertEqual(expected, result)

    def test_get_type_species_null(self):
        result = get_type_species(None)
        expected = ''
        self.assertEqual(expected, result)

    def test_get_sex_null(self):
        result = get_sex(None)
        expected = ''
        self.assertEqual(expected, result)

    def test_get_sex_worker(self):
        result = get_sex('w')
        expected = 'worker'
        self.assertEqual(expected, result)

    def test_get_voucher_state(self):
        result = get_voucher_state('')
        expected = ''
        self.assertEqual(expected, result)
