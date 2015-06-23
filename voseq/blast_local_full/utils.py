import os
import uuid

from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from blast_local.utils import BLAST
from public_interface.models import Sequences


class BLASTFull(BLAST):
    """
    Class to handle duties related to local blast against all sequences in our
    database.

    The database is `masked` by default, to eliminate low-complexity regions
    from the sequences.

    Use `mask=False` to create unmasked blast databases.
    """
    def __init__(self, blast_type, voucher_code, gene_code, mask=None):
        self.e_value = 0.001
        self.blast_type = blast_type
        self.voucher_code = voucher_code
        self.gene_code = gene_code
        self.cwd = os.path.dirname(__file__)

        if mask is not False:
            self.mask = True
        else:
            self.mask = False

        self.path = os.path.join(self.cwd,
                                 'db',
                                 'full_db_seqs.fas.n*',
                                 )
        self.db = os.path.join(self.cwd,
                               'db',
                               'full_db_seqs.fas',
                               )
        self.query_file = os.path.join(self.cwd,
                                       'db',
                                       'query_' + uuid.uuid4().hex + '.fas',
                                       )
        self.output_file = os.path.join(self.cwd,
                                        'db',
                                        'output_' + uuid.uuid4().hex + '.xml',
                                        )

    def save_seqs_to_file(self):
        """
        Query all sequences from our database and save them to local
        disk.

        Sets attribute `self.seq_file` containing necessary sequences from our
        database.
        """
        if self.blast_type == 'full':
            self.seq_file = os.path.join(self.cwd,
                                         'db',
                                         'full_db_seqs.fas',
                                         )
            queryset = Sequences.objects.all()

            my_records = []
            for i in queryset:
                item_id = i.code_id + '|' + i.gene_code
                seq = self.strip_question_marks(i.sequences)
                if seq != '':
                    seq_record = SeqRecord(Seq(seq), id=item_id)
                    my_records.append(seq_record)
            SeqIO.write(my_records, self.seq_file, "fasta")
