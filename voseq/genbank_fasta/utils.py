import json
import uuid

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

from public_interface.models import Vouchers
from public_interface.models import Sequences
from public_interface.models import Genes
from core import utils


def get_voucher_codes(cleaned_data):
    voucher_codes = []
    if cleaned_data['taxonset'] is not None:
        voucher_codes = json.loads(cleaned_data['taxonset'].taxonset_list)
    if cleaned_data['voucher_codes'] != '':
        voucher_codes += cleaned_data['voucher_codes'].splitlines()
    return set(voucher_codes)


def get_gene_codes(cleaned_data):
    gene_codes = []
    if cleaned_data['geneset'] is not None:
        gene_codes = json.loads(cleaned_data['geneset'].geneset_list)
    if len(cleaned_data['gene_codes']) > 0:
        gene_codes += [i.gene_code for i in cleaned_data['gene_codes']]
    return set(gene_codes)


class Results(object):
    """Returns:
    * List of items with accession numbers that will not be included in
      FASTA or protein files (code, gene_code, accession).
    * FASTA dataset as string.
    * Protein dataset as string.

    Usage:
        res = Results(voucher_codes, gene_codes)
        res.get_datasets()
        fasta_dataset = res.fasta
        protein_dataset = res.protein
        items_with_accession = res.items_with_accession
    """
    def __init__(self, voucher_codes, gene_codes):
        self.voucher_codes = voucher_codes
        self.gene_codes = gene_codes
        self.items_with_accession = []
        self.guid = self.make_guid()
        self.fasta = ''
        self.protein = ''
        self.fasta_file = 'fasta_' + self.guid + '.fasta'
        self.protein_file = 'prot_' + self.guid + '.fasta'

    def get_datasets(self):
        """Queries sequences and creates FASTA, protein strings and list of
        items with accession number (code, gene_code, accession).
        """
        for code in self.voucher_codes:
            try:
                v = Vouchers.objects.get(code=code)
            except Vouchers.DoesNotExist:
                continue

            for gene_code in self.gene_codes:
                if v:
                    try:
                        s = Sequences.objects.get(code=v, gene_code=gene_code)
                    except Sequences.DoesNotExist:
                        continue

                    try:
                        g = Genes.objects.get(gene_code=gene_code)
                    except Genes.DoesNotExist:
                        continue

                    if s.accession.strip() != '':
                        self.items_with_accession.append((code, gene_code, s.accession))
                    else:
                        seq_id = v.genus + '_' + v.species + '_' + code
                        seq_description = '[org=' + v.genus + ' ' + v.species + ']'
                        seq_description += ' [Specimen-voucher=' + v.code + ']'
                        seq_description += ' [note=' + g.description + ' gene, partial cds.]'
                        seq_description += ' [Lineage=]'
                        seq_seq = s.sequences

                        # # DNA sequences
                        seq_seq = utils.strip_question_marks(seq_seq)[0]
                        if '?' in seq_seq or 'N' in seq_seq.upper():
                            seq_obj = Seq(seq_seq, IUPAC.ambiguous_dna)
                        else:
                            seq_obj = Seq(seq_seq, IUPAC.unambiguous_dna)

                        self.fasta += '>' + seq_id + ' ' + seq_description + '\n'
                        self.fasta += str(seq_obj) + '\n'

                        # # Protein sequences
                        seq_seq, removed = utils.strip_question_marks(s.sequences)

                        if int(g.reading_frame) == 1:
                            if removed % 3 == 0:
                                start_translation = 0
                            if removed % 3 == 1:
                                start_translation = 2
                            if removed % 3 == 2:
                                start_translation = 1

                        if int(g.reading_frame) == 2:
                            if removed % 3 == 0:
                                start_translation = 1
                            if removed % 3 == 1:
                                start_translation = 0
                            if removed % 3 == 2:
                                start_translation = 2

                        if int(g.reading_frame) == 3:
                            if removed % 3 == 0:
                                start_translation = 2
                            if removed % 3 == 1:
                                start_translation = 1
                            if removed % 3 == 2:
                                start_translation = 0

                        if '?' in seq_seq or 'N' in seq_seq.upper():
                            seq_obj = Seq(seq_seq[start_translation:], IUPAC.ambiguous_dna)
                        else:
                            seq_obj = Seq(seq_seq[start_translation:], IUPAC.unambiguous_dna)
                        prot_sequence = seq_obj.translate(table=g.genetic_code)

                        self.protein += '>' + seq_id + ' ' + seq_description + '\n'
                        self.protein += str(prot_sequence) + '\n'

    def make_guid(self):
        return uuid.uuid4().hex
