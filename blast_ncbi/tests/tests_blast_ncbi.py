import copy
from io import StringIO
import os
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.core.management import call_command

from blast_ncbi.utils import BLASTNcbi


TEST_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(TEST_PATH, "CP100-10_COI-begin.xml"), "r") as handle:
    ncbi_return_handle1 = StringIO(handle.read())
    ncbi_return_handle2 = copy.copy(ncbi_return_handle1)


class TestNcbiBlast(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        self.blast = BLASTNcbi(blast_type="remote", voucher_code="CP100-10",
                               gene_code="COI-begin")

    @patch("Bio.Blast.NCBIWWW.qblast", return_value=ncbi_return_handle1)
    def test_blast_with_accession_number_in_header(self, mock_qblast):
        self.blast.save_query_to_file()
        self.blast.do_blast()
        result = self.blast.parse_blast_output()
        self.blast.delete_query_output_files()
        self.assertTrue(len(result) > 0)

    @patch("Bio.Blast.NCBIWWW.qblast", return_value=ncbi_return_handle2)
    def test_index(self, mock_blast):
        response = self.client.get('/blast_ncbi/CP100-10/COI-begin/', follow=True)
        self.assertEqual(200, response.status_code)
