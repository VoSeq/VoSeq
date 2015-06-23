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
        make_option('--prefix',
                    dest='prefix',
                    help='If your tables of VoSeq have been prefixed you can specify it here.',
                    ),
    )

    def handle(self, *args, **options):
        if options['dumpfile'] is None:
            error_msg = 'Enter name of database dump file as argument.' \
                        ' "python manage.py migrate_db --dumpfile=dump.xml --settings=voseq.settings.local. ' \
                        'You can also use "--prefix voseq_" if your tables have any prepended prefix. ' \
                        'This file can be obtained from your MySQL database using this command:' \
                        ' "mysqdump --xml database > dump.xml"'
            raise CommandError(error_msg)

        dump_file = options['dumpfile']
        tables_prefix = options['prefix']
        verbosity = options['verbosity']

        with codecs.open(dump_file, "r") as handle:
            dump = handle.read()

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

        parser.save_table_members_to_db()
