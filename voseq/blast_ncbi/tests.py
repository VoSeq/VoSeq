from django.test import TestCase
from django.core.management import call_command

from blast_ncbi.utils import BLASTNcbi


class TestNcbiBlast(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        voucher_code = 'CP100-10'
        gene_code = 'COI'
        self.blast = BLASTNcbi(voucher_code, gene_code)

    def test_blast_with_accession_number_in_header(self):
        self.blast.save_query_to_file()
        self.blast.do_blast()
        result = self.blast.parse_blast_output()
        self.blast.delete_query_output_files()
        self.assertTrue(len(result) > 0)
