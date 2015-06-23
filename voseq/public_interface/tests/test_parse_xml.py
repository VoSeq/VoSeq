import datetime
import pytz

from django.test import TestCase

from public_interface.management.commands.migrate_db import ParseXML


class TestParseXML(TestCase):
    def setUp(self):
        with open('test_db_dump.xml') as handle:
            self.xml_string = handle.read()

        self.parse_xml_to_fail = ParseXML(xml_string=self.xml_string, tables_prefix='voseq_',
                                          verbosity=0)
        self.parse_xml = ParseXML(xml_string=self.xml_string, tables_prefix='',
                                  verbosity=0)

    def test_parse_table_genes(self):
        """We don't have tables with prefix 'voseq_' in our test_db_dump.xml file
        """
        self.assertRaises(ValueError, self.parse_xml_to_fail.parse_table_genes, self.xml_string)

    def test_parse_timestamp_good(self):
        """Make some sense of the multiple datetimes and timestamps that we have
        in the MySQL databases.
        """
        TZINFO = pytz.utc

        timestamp = '2014-10-01 10:20:45'
        expected = datetime.datetime(2014, 10, 1, 10, 20, 45, tzinfo=TZINFO)
        result = self.parse_xml.parse_timestamp(timestamp, 'good')
        self.assertEqual(expected, result)

    def test_parse_timestamp_bad(self):
        timestamp = '0000-00-00 00:00:00'
        expected = None
        result = self.parse_xml.parse_timestamp(timestamp, 'bad')
        self.assertEqual(expected, result)

    def test_parse_timestamp_null(self):
        timestamp = None
        expected = None
        result = self.parse_xml.parse_timestamp(timestamp, 'null')
        self.assertEqual(expected, result)

    def test_parse_timestamp_null_verbose(self):
        timestamp = None
        expected = None
        self.parse_xml.verbosity = 1
        result = self.parse_xml.parse_timestamp(timestamp, 'null_verbose')
        self.assertEqual(expected, result)
