import datetime
import glob
import logging
import os
import re
import subprocess
from typing import Dict, Any, Tuple
import uuid

from django.conf import settings
from django.http import HttpRequest
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
from Bio.Blast import NCBIXML
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import pytz

from . import exceptions
from stats.models import Stats
from public_interface.models import Sequences


log = logging.getLogger(__name__)


def get_voucher_codes(cleaned_data) -> Tuple[str]:
    """Processes list of voucher codes entered by users.

    It receives data from a **Form class** (`cleaned_data`) and makes sure that
    there are not duplicated voucher codes passed to the dataset builder.
    It also drops voucher codes if specified by users using the double dash:
    `--CP100-10`.

    Args:
        * `form.cleaned_data`: taken from a Form class

    Returns:
        tuple of voucher codes, no dupes, dropped unwanted.
    """
    voucher_codes = tuple()
    if cleaned_data['taxonset'] is not None:
        voucher_codes += tuple(cleaned_data['taxonset'].taxonset_list.splitlines())
    if cleaned_data['voucher_codes'] != '':
        voucher_codes += tuple(cleaned_data['voucher_codes'].splitlines())

    voucher_codes_clean = set()
    for i in voucher_codes:
        if re.search(r'^--', i):
            i_clean = re.sub(r'^--', '', i)
            voucher_codes_clean.add(i_clean)
        else:
            voucher_codes_clean.add(i)

    voucher_codes_set = set([i for i in voucher_codes_clean if i.strip()])

    vouchers_to_drop = []
    for i in voucher_codes:
        if re.search(r'^--', i):
            vouchers_to_drop.append(re.sub(r'^--', '', i))

    voucher_codes_filtered = tuple()
    for i in voucher_codes_set:
        if i not in vouchers_to_drop:
            voucher_codes_filtered += (i,)
    return tuple(sorted(voucher_codes_filtered))


def get_gene_codes(cleaned_data):
    """Processes list of gene codes entered by users.

    It receives data from a **Form class** (`cleaned_data`) and makes sure that
    there are not duplicated gene codes passed to the dataset builder.

    Args:
        * `form.cleaned_data`: taken from a Form class

    Returns:
        set of gene codes, sorted, no duplicates.
    """
    gene_codes = []
    if cleaned_data['geneset'] is not None:
        geneset_list = cleaned_data['geneset'].geneset_list.splitlines()
        for i in geneset_list:
            if i not in gene_codes:
                gene_codes.append(i)

    if cleaned_data['gene_codes']:
        for i in cleaned_data['gene_codes']:
            if i.gene_code not in gene_codes:
                gene_codes.append(i.gene_code)

    return tuple(sorted(gene_codes, key=str.lower))


def get_context(request: HttpRequest) -> Dict[str, Any]:
    version, stats = get_version_stats()
    context = {
        "username": get_username(request),
        "version": version,
        "stats": stats,
        "app_name": settings.APP_NAME.title(),
    }
    return context


def get_version_stats():
    """Returns version and database statistics for page footer."""
    version = settings.VERSION
    try:
        stats = Stats.objects.get(pk=1)
    except Stats.DoesNotExist:
        stats = ''
    return version, stats


def get_username(request: HttpRequest) -> str:
    username = 'Guest'
    if request.user.is_authenticated:
        username = request.user.username
    return username


def clean_positions(a_list):
    if 'ALL' in a_list:
        return ['ALL']
    elif '1st' in a_list and '2nd' in a_list and '3rd' in a_list:
        return ['ALL']
    elif '1st' in a_list and '2nd' in a_list and '3rd' not in a_list:
        return ['1st-2nd']
    elif len(a_list) == 2:  # 1st and 3rd, or 2nd and 3rd
        raise exceptions.InadequateCodonPositions(
            "Cannot create dataset for only codon positions {0} and {1}."
            "".format(a_list[0], a_list[1])
        )
    else:
        return a_list


class BLAST(object):
    """Handle duties related to local blasts.

    Blasts against sequences of one gene, and full blast against all sequences
    in our database.

    The database is `masked` by default, to eliminate low-complexity regions
    from the sequences.

    Use `mask=False` to create unmasked blast databases.

    """
    def __init__(self, blast_type, voucher_code, gene_code, mask=None):
        """Type of blast to do: local, full, remote.

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
        self.mask = bool(mask)
        self.path = os.path.join(settings.MEDIA_ROOT, 'db',
                                 "{0}_seqs.fas.n*".format(self.gene_code))

        self.db = os.path.join(settings.MEDIA_ROOT, 'db',
                               "{0}_seqs.fas".format(self.gene_code))

        self.query_file = os.path.join(settings.MEDIA_ROOT, 'db',
                                       "query_{0}.fas".format(uuid.uuid4().hex))

        self.output_file = os.path.join(settings.MEDIA_ROOT, 'db',
                                        "output_{0}.xml".format(uuid.uuid4().hex))
        if settings.OS == 'linux':
            self.bin_path = '/usr/bin/'
        else:
            self.bin_path = '/usr/local/ncbi/blast/bin/'

    def have_blast_db(self):
        """Finds out whether we already have a blast db with our sequences.

        :return: True or False

        """
        files = glob.glob(self.db + '.*')
        return bool(files)

    def is_blast_db_up_to_date(self):
        """Finds out whether our blast db contains all our sequences.

        In other words, it finds out whether there are sequences in our postgres
        db with time_created or time_edited more recent than our blast db files.

        :return: True or False
        """
        if not self.have_blast_db():
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
        """Query sequences for each gene from database and save them to local disk.

        Sets attribute `self.seq_file` containing necessary sequences from our
        database.

        """
        if self.blast_type == 'local':
            self.seq_file = os.path.join(settings.MEDIA_ROOT,
                                         'db',
                                         "{0}_seqs.fas".format(self.gene_code))
            queryset = Sequences.objects.all().filter(gene__gene_code=self.gene_code)

            my_records = []
            for i in queryset:
                item_id = i.code_id + '|' + i.gene.gene_code
                seq = self.strip_question_marks(i.sequences)
                if seq != '':
                    seq_record = SeqRecord(Seq(seq), id=item_id)
                    my_records.append(seq_record)
            SeqIO.write(my_records, self.seq_file, "fasta")

    def create_blast_db(self):
        """Creates a BLAST database from our sequences file in FASTA format.

        Optionally eliminates low-complexity regions from the sequences.

        """
        log.debug("Creating blast db")
        if self.mask:
            command = self.bin_path
            command += 'dustmasker -in ' + self.seq_file + ' -infmt fasta '
            command += '-outfmt maskinfo_asn1_bin -out ' + self.seq_file + '_dust.asnb'
            subprocess.check_output(command, shell=True)  # identifying low-complexity regions.

            command = self.bin_path
            command += 'makeblastdb -in ' + self.seq_file + ' -input_type fasta -dbtype nucl '
            command += '-mask_data ' + self.seq_file + '_dust.asnb '
            command += '-out ' + self.seq_file + ' -title "Whole Genome without low-complexity regions"'  # noqa
            subprocess.check_output(command, shell=True)  # Overwriting the genome file.
        else:
            command = self.bin_path
            command += 'makeblastdb -in ' + self.seq_file + ' -input_type fasta -dbtype nucl '
            command += '-out ' + self.seq_file + ' -title "Whole Genome unmasked"'
            subprocess.check_output(command, shell=True)

    def save_query_to_file(self) -> bool:
        """Returns boolean to point out whether we could save a query file"""
        seq_obj = Sequences.objects.filter(
            code_id=self.voucher_code, gene__gene_code=self.gene_code
        ).first()
        this_id = '{0}|{1}'.format(seq_obj.code_id, seq_obj.gene.gene_code)
        seq = self.strip_question_marks(seq_obj.sequences)

        if seq:
            seq_record = SeqRecord(Seq(seq), id=this_id)
            SeqIO.write(seq_record, self.query_file, "fasta")
            return True
        else:
            return False

    def do_blast(self):
        blastn_cline = NcbiblastnCommandline(
            cmd=self.bin_path + 'blastn',
            query=self.query_file,
            db=self.db,
            evalue=self.e_value,
            outfmt=5,
            out=self.output_file
        )
        blastn_cline()
        return self.output_file

    def parse_blast_output(self):
        """Returns list of dictionaries with data:

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

    def strip_question_marks(self, seq: str) -> str:
        seq = re.sub('^\?+', '', seq)
        seq = re.sub('\?+$', '', seq)

        seq = re.sub('^N+', '', seq)
        seq = re.sub('N+$', '', seq)
        seq = seq.replace('-', 'N')
        seq = seq.replace('?', 'N')
        return seq.strip()
