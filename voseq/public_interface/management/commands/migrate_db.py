import codecs
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from ._migrate_db import ParseXML


class Command(BaseCommand):
    """
    Runs the _migrate_db.py script.
    """
    option_list = BaseCommand.option_list + (
        make_option('--dumpfile',
                    dest='dumpfile',
                    help='Enter name of database dump file as argument.'
                         'This file can be obtained from your MySQL database using this command:'
                         '\t"mysqdump --xml database > dump.xml"',
                    ),
    )

    def handle(self, *args, **options):
        if options['dumpfile'] is None:
            error_msg = 'Enter name of database dump file as argument.' \
                        ' "python manage.py migrate_db --dumpfile=dump.xml --settings=voseq.settings.local' \
                        'This file can be obtained from your MySQL database using this command:' \
                        ' "mysqdump --xml database > dump.xml"',
            raise CommandError(error_msg)

        dump_file = options['dumpfile']
        verbosity = options['verbosity']

        with codecs.open(dump_file, "r") as handle:
            dump = handle.read()

        # tables_prefix = 'voseq_'
        tables_prefix = ''
        parser = ParseXML(dump, tables_prefix, verbosity)

        parser.import_table_vouchers()
        parser.save_table_vouchers_to_db()

        parser.import_table_sequences()
        parser.save_table_sequences_to_db()

        parser.import_table_primers()
        parser.save_table_primers_to_db()

        parser.save_table_genes_to_db()

        parser.save_table_genesets_to_db()

        parser.save_table_taxonsets_to_db()
