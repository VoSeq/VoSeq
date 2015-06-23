import datetime
import glob
import os
import re
import subprocess
import uuid

from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pytz

from public_interface.models import Sequences


class BLAST(object):
    """
    Class to handle duties related to local blast against sequences of one gene,
    and full blast against all sequences in our database.

    The database is `masked` by default, to eliminate low-complexity regions
    from the sequences.

    Use `mask=False` to create unmasked blast databases.
    """
    def __init__(self, blast_type, voucher_code, gene_code, mask=None):
        """
        Type of blast to do: local, full, remote

        :param blast_type: local, full, remote.
        :param voucher_code:
        :param gene_code:
        """
        self.e_value = 0.001
        self.blast_type = blast_type
        self.voucher_code = voucher_code
        self.gene_code = gene_code
        self.cwd = os.path.dirname(__file__)
        self.seq_file = ""

        if mask is not False:
            self.mask = True
        else:
            self.mask = False

        self.path = os.path.join(self.cwd,
                                 'db',
                                 self.gene_code + '_seqs.fas.n*',
                                 )
        self.db = os.path.join(self.cwd,
                               'db',
                               self.gene_code + '_seqs.fas',
                               )
        self.query_file = os.path.join(self.cwd,
                                       'db',
                                       'query_' + uuid.uuid4().hex + '.fas',
                                       )
        self.output_file = os.path.join(self.cwd,
                                        'db',
                                        'output_' + uuid.uuid4().hex + '.xml',
                                        )

    def have_blast_db(self):
        """
        Finds out whether we already have a blast db with our sequences.

        :return: True or False
        """
        files = glob.glob(self.db + '.*')
        if len(files) > 0:
            return True
        else:
            return False

    def is_blast_db_up_to_date(self):
        """
        Finds out whether our blast db contains all our sequences. In other
        words, it finds out whether there are sequences in our postgres db with
        time_created or time_edited more recent than our blast db files.

        :return: True or False
        """
        if self.have_blast_db() is False:
            return False

        # get time creation blast database files
        modification_times = []
        files = glob.glob(self.path)
        for i in files:
            mod_time_in_secs = os.stat(i).st_ctime
            modification_times.append(datetime.datetime.fromtimestamp(mod_time_in_secs))
        modification_times.sort(reverse=True)
        time_creation_blast = modification_times[0].replace(tzinfo=pytz.utc)

        # get time creation time edited sequences in our database
        time_created_queryset = Sequences.objects.all().order_by('-time_created')[:1]
        time_created = time_created_queryset[0].time_created

        time_edited_queryset = Sequences.objects.all().order_by('-time_edited')[:1]
        time_edited = time_edited_queryset[0].time_edited

        if time_created > time_creation_blast or time_edited > time_creation_blast:
            return False
        else:
            return True

    def save_seqs_to_file(self):
        """
        Query sequences for each gene from our database and save them to local
        disk.

        Sets attribute `self.seq_file` containing necessary sequences from our
        database.
        """
        if self.blast_type == 'local':
            self.seq_file = os.path.join(self.cwd,
                                         'db',
                                         self.gene_code + "_seqs.fas",
                                         )
            queryset = Sequences.objects.all().filter(gene_code=self.gene_code)

            my_records = []
            for i in queryset:
                item_id = i.code_id + '|' + i.gene_code
                seq = self.strip_question_marks(i.sequences)
                if seq != '':
                    seq_record = SeqRecord(Seq(seq), id=item_id)
                    my_records.append(seq_record)
            SeqIO.write(my_records, self.seq_file, "fasta")

    def create_blast_db(self):
        """
        Creates a BLAST database from our sequences file in FASTA format.
        Optionally eliminates low-complexity regions from the sequences.

        :return:
        """
        print("Creating blast db")
        if self.mask is True:
            command = 'dustmasker -in ' + self.seq_file + ' -infmt fasta '
            command += '-outfmt maskinfo_asn1_bin -out ' + self.seq_file + '_dust.asnb'
            subprocess.check_output(command, shell=True)  # identifying low-complexity regions.

            command = 'makeblastdb -in ' + self.seq_file + ' -input_type fasta -dbtype nucl '
            command += '-mask_data ' + self.seq_file + '_dust.asnb '
            command += '-out ' + self.seq_file + ' -title "Whole Genome without low-complexity regions"'
            subprocess.check_output(command, shell=True)  # Overwriting the genome file.
        else:
            command = 'makeblastdb -in ' + self.seq_file + ' -input_type fasta -dbtype nucl '
            command += '-out ' + self.seq_file + ' -title "Whole Genome unmasked"'
            subprocess.check_output(command, shell=True)

    def save_query_to_file(self):
        b = Sequences.objects.get(code_id=self.voucher_code, gene_code=self.gene_code)
        this_id = b.code_id + '|' + b.gene_code
        seq = self.strip_question_marks(b.sequences)

        if seq != '':
            seq_record = SeqRecord(Seq(seq),
                                   id=this_id)
            SeqIO.write(seq_record, self.query_file, "fasta")

    def do_blast(self):
        blastn_cline = NcbiblastnCommandline(query=self.query_file, db=self.db,
                                             evalue=self.e_value, outfmt=5, out=self.output_file)
        blastn_cline()
        return self.output_file

    def parse_blast_output(self):
        """
        Returns list of dictionaries with data:

        match_description, max_score, total_score, query_cover, e_value, % ident, accession number
        """
        handle = open(self.output_file, 'r')
        blast_record = NCBIXML.read(handle)
        hits = []
        append = hits.append

        for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                if hsp.expect < self.e_value:
                    obj = {}

                    # This is for our local blasts
                    obj['description'] = alignment.title.split(' ')[1]
                    if '|' in obj['description']:
                        obj['voucher_code'] = obj['description'].split('|')[0]
                        obj['gene_code'] = obj['description'].split('|')[1]
                    # This is for the NCBI blasts that need parsing of alignment.title
                    else:
                        description = alignment.title
                        res = re.search('gi\|.+\|.+\|([A-Z]+[0-9]+)\.[0-9]+\|\s*(.+)', description)
                        if res:
                            obj['accession'], obj['description'] = res.groups()
                        else:
                            obj['description'] = alignment.title

                    obj['score'] = hsp.score
                    obj['bits'] = hsp.bits
                    obj['e_value'] = hsp.expect

                    obj['query_length'] = blast_record.query_length
                    obj['align_length'] = hsp.align_length
                    obj['identities'] = hsp.identities

                    obj['query_cover'] = round((obj['align_length'] * 100) / obj['query_length'], 1)
                    obj['ident'] = round((obj['identities'] * 100) / obj['align_length'], 1)
                    append(obj)
        return hits

    def delete_query_output_files(self):
        if os.path.isfile(self.query_file):
            os.remove(self.query_file)

        if os.path.isfile(self.output_file):
            os.remove(self.output_file)

    def strip_question_marks(self, seq):
        seq = re.sub('^\?+', '', seq)
        seq = re.sub('\?+$', '', seq)

        seq = re.sub('^N+', '', seq)
        seq = re.sub('N+$', '', seq)
        seq = seq.replace('-', 'N')
        seq = seq.replace('?', 'N')
        return seq
