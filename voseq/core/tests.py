from django.test import TestCase
from django.core.management import call_command

from core.utils import strip_question_marks


class TestCore(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_strip_question_marks_n(self):
        seq = '?NNNNNACTACGATGCRGCAST'
        result = strip_question_marks(seq)
        expected = ('ACTACGATGCRGCAST', 6)
        self.assertEqual(expected, result)
