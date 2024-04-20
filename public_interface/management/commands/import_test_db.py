"""Import test database with sample data for testing or developing"""
import codecs
import os
from django.core.management.base import BaseCommand

from ._migrate_db import ParseXML


class Command(BaseCommand):
    def handle(self, *args, **options):
        dump_file = os.path.join(os.path.abspath(os.path.curdir), 'test_db_dump.xml')
        with codecs.open(dump_file, "r") as handle:
            dump = handle.read()

        parser = ParseXML(dump)

        parser.import_table_vouchers()
        parser.save_table_vouchers_to_db()

        parser.import_table_sequences()
        parser.save_table_sequences_to_db()

        parser.import_table_primers()
        parser.save_table_primers_to_db()

        parser.save_table_genes_to_db()

        parser.save_table_genesets_to_db()

        parser.save_table_taxonsets_to_db()

        parser.save_table_members_to_db()
