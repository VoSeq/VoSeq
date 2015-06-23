import os
import uuid

from Bio.Blast import NCBIWWW

from blast_local.utils import BLAST


class BLASTNcbi(BLAST):
    """
    Class to handle duties related to blast against sequences in NCBI Genbank.
    """
    def __init__(self, voucher_code, gene_code):
        self.voucher_code = voucher_code
        self.gene_code = gene_code
        self.e_value = 0.001
        self.cwd = os.path.dirname(__file__)
        self.query_file = os.path.join(self.cwd,
                                       'db',
                                       'query_' + uuid.uuid4().hex + '.fas',
                                       )
        self.output_file = os.path.join(self.cwd,
                                        'db',
                                        'output_' + uuid.uuid4().hex + '.xml',
                                        )

    def do_blast(self):
        """
        Does a blast against NCBI and saves returned XML file to local disk.
        """
        with open(self.query_file) as handle:
            fasta_string = handle.read()

        result_handle = NCBIWWW.qblast('blastn', 'nt', fasta_string)

        with open(self.output_file, 'w') as writer:
            writer.write(result_handle.read())
        result_handle.close()
