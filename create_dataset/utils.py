import logging
import re

from seqrecord_expanded import SeqRecordExpanded
from seqrecord_expanded.exceptions import MissingParameterError, TranslationErrorMixedGappedSeq
from dataset_creator import Dataset
from create_dataset.models import Dataset as DatasetModel
from Bio.Nexus.Nexus import NexusError

from core import exceptions
from core.utils import get_voucher_codes, get_gene_codes, clean_positions
from .nexus import DatasetHandler
from public_interface.models import Genes, Sequences, Vouchers


log = logging.getLogger(__name__)


LINEAGES = {
    # superfamily: lineage from domain Eukaryota to suborder Ditrysia
    "Papilionoidea": "Eukaryota; Metazoa; Ecdysozoa; Arthropoda; Hexapoda; Insecta; Pterygota; Neoptera; Holometabola; Lepidoptera; Glossata; Ditrysia; ",  # noqa
    "Hesperioidea": "Eukaryota; Metazoa; Ecdysozoa; Arthropoda; Hexapoda; Insecta; Pterygota; Neoptera; Holometabola; Lepidoptera; Glossata; Ditrysia; ",  # noqa
    "Hedyloidea": "Eukaryota; Metazoa; Ecdysozoa; Arthropoda; Hexapoda; Insecta; Pterygota; Neoptera; Holometabola; Lepidoptera; Glossata; Ditrysia; ",  # noqa
}


class CreateDataset(object):
    """Accepts form input to create a dataset in several formats.

    Also codon positions, for list of codes and genes. Takes into account the
    vouchers passed as taxonset.

    Attributes:
        ``codon_positions``: For now is a list. It is cleaned to avoid redundant
                      information such as having ['ALL', '1st'] in there as 'ALL'
                      overrides '1st'.
        ``seq_objs``: Ordered_dict by gene_code. Keys are gene_codes and values
                      are tuples containing BioPython seq_record objects:
                      seq=Seq('????CAGATAAAS'),
                      id='CP13-01_Genus_Species',
                      name='CAD',  # gene_code
                      description='CP13-01',  # voucher code

        ``dataset_str``: output dataset to pass to users.

    """
    def __init__(self, cleaned_data, dataset_obj_id=None):
        # skip sequences with accession numbers and building GenBank Fasta file
        self.dataset_obj_id = dataset_obj_id
        self.sequences_skipped = []
        self.cleaned_data = cleaned_data
        self.translations = None
        self.degen_translations = None
        self.clean_translations()

        self.errors = []
        self.seq_objs = []
        self.minimum_number_of_genes = cleaned_data['number_genes']
        self.aminoacids = cleaned_data['aminoacids']

        try:
            self.codon_positions = clean_positions(cleaned_data['positions'])
        except exceptions.InadequateCodonPositions as e:
            self.codon_positions = None
            self.errors = [e]

        self.file_format = cleaned_data['file_format']
        self.partition_by_positions = cleaned_data['partition_by_positions']
        self.voucher_codes = get_voucher_codes(cleaned_data)
        self.gene_codes = get_gene_codes(cleaned_data)
        self.gene_codes_and_lengths = None
        self.taxon_names = cleaned_data['taxon_names']
        self.voucher_codes_metadata = dict()
        self.gene_codes_metadata = self.get_gene_codes_metadata()
        self.warnings = []
        self.outgroup = cleaned_data['outgroup']
        self.dataset_file = None
        self.aa_dataset_file = None
        self.charset_block = None
        self.dataset_str = self.create_dataset()

    def clean_translations(self):
        if self.cleaned_data['translations']:
            self.degen_translations = self.cleaned_data['degen_translations']
        else:
            # No need to do degen translation
            self.degen_translations = None

    def create_dataset(self):
        if not self.codon_positions:
            return ''

        error_msg = None
        if self.degen_translations is not None and self.codon_positions != ['ALL']:
            error_msg = 'Cannot degenerate codons if you have not selected all codon positions'
            self.errors.append(error_msg)
        elif self.degen_translations is not None and self.partition_by_positions != 'by gene':
            error_msg = 'Cannot degenerate codons if they go to different partitions'
            self.errors.append(error_msg)

        if error_msg:
            return ''

        self.voucher_codes = get_voucher_codes(self.cleaned_data)
        self.gene_codes = get_gene_codes(self.cleaned_data)
        self.create_seq_objs()

        supported_formats = [
            'NEXUS', 'GenBankFASTA', 'FASTA', 'MEGA', 'TNT', 'PHYLIP', 'Bankit'
        ]
        if self.file_format in supported_formats:
            try:
                dataset = Dataset(
                    self.seq_objs,
                    format=self.file_format,
                    partitioning=self.partition_by_positions,
                    codon_positions=self.codon_positions[0],
                    aminoacids=self.aminoacids,
                    degenerate=self.degen_translations,
                    outgroup=self.outgroup,
                )
            except (MissingParameterError, ValueError, TranslationErrorMixedGappedSeq) as e:
                self.errors.append(e)
                dataset = None
            except NexusError as e:
                self.errors.append(e.__str__())
                dataset = None

            if not dataset:
                return ""

            self.warnings += dataset.warnings
            dataset_handler = DatasetHandler(dataset.dataset_str, self.file_format)
            self.dataset_file = dataset_handler.dataset_file

            if self.file_format == 'PHYLIP':
                self.charset_block = dataset.extra_dataset_str

            return dataset.dataset_str

    def create_seq_objs(self):
        """Generate a list of SeqRecord-expanded objects"""
        our_taxon_names = self.get_taxon_names_for_taxa()
        all_seqs = self.get_all_sequences()
        all_seqs_count = all_seqs.count()

        idx = 0
        for gene_code in self.gene_codes:
            for voucher_code in self.voucher_codes:
                idx += 1
                sequence = all_seqs.filter(code_id=voucher_code, gene__gene_code=gene_code)
                if idx % 100 == 0:
                    if self.dataset_obj_id:
                        DatasetModel.objects.filter(id=self.dataset_obj_id).update(
                            progress=f"{idx}/{all_seqs_count}"
                        )
                    log.info(
                        f'{idx}/{all_seqs_count} processing dataset {sequence["code_id"]} '
                        f'{sequence["gene__gene_code"]}'
                    )

                if not sequence.exists():
                    seq_obj = self.build_seq_obj(
                        voucher_code,
                        gene_code,
                        accession_number='',
                        our_taxon_names=our_taxon_names,
                        all_seqs=all_seqs,
                    )
                else:
                    sequence = sequence.first()
                    seq_obj = self.build_seq_obj(
                        sequence['code_id'],
                        sequence['gene__gene_code'],
                        sequence['accession'],
                        our_taxon_names,
                        all_seqs,
                    )

                if seq_obj is None:
                    self.warnings += ['Could not find voucher {0}'.format(sequence['code_id'])]
                    continue
                if self.file_format == "GenBankFASTA" and seq_obj.accession_number:
                    log.debug("Skipping seq {} {} because it has accession number {}"
                              "".format(seq_obj.voucher_code, seq_obj.gene_code,
                                        seq_obj.accession_number))
                    self.sequences_skipped.append({
                        "code": seq_obj.voucher_code,
                        "gene_code": seq_obj.gene_code,
                        "accession_number": seq_obj.accession_number,
                    })
                else:
                    self.seq_objs.append(seq_obj)

    def get_all_sequences(self):
        """Return sequences as dict of lists containing sequence and related data.
        """
        all_seqs = Sequences.objects.filter(
            code__in=self.voucher_codes,
            gene__gene_code__in=self.gene_codes,
        ).values('code_id', 'gene__gene_code', 'sequences', 'accession').order_by('code_id')
        return all_seqs

    def build_seq_obj(self, code, gene_code, accession_number, our_taxon_names, all_seqs):
        """Builds a SeqRecordExpanded object. If cannot be built, returns None.

        """
        this_voucher_seqs = self.extract_sequence_from_all_seqs_in_db(all_seqs, code, gene_code)

        if this_voucher_seqs == '?':
            seq = '?' * self.gene_codes_metadata[gene_code]['length']
        else:
            seq = self.create_seq_record(this_voucher_seqs, gene_code)

        if code in our_taxon_names:
            lineage = self.get_lineage(code)
            seq_record = SeqRecordExpanded(
                seq,
                voucher_code=code.replace(" ", "_"),
                taxonomy=our_taxon_names[code],
                gene_code=gene_code,
                reading_frame=self.gene_codes_metadata[gene_code]['reading_frame'],
                table=self.gene_codes_metadata[gene_code]['genetic_code'],
                lineage=lineage,
                accession_number=accession_number,
            )
            return seq_record
        else:
            return None

    def get_lineage(self, code):
        voucher = Vouchers.objects.get(code=code)
        try:
            lineage = LINEAGES[voucher.superfamily]
        except KeyError:
            lineage = ""

        additional_lineage = ";".join([
            voucher.family, voucher.subfamily, voucher.tribe, voucher.subtribe,
            voucher.genus, voucher.species, voucher.subspecies,
        ])
        lineage += re.sub(";+", "; ", additional_lineage)
        return lineage.strip()

    def extract_sequence_from_all_seqs_in_db(self, all_seqs, code, gene_code):
        try:
            voucher_sequences = all_seqs.filter(code_id=code)
        except KeyError:
            self.warnings += [
                'Could not find sequences for voucher {0} and gene_code {1}'.format(
                    code, gene_code)]
            return '?'

        try:
            this_voucher_seqs = voucher_sequences.filter(
                gene__gene_code=gene_code,
            ).first()['sequences']
        except (AttributeError, KeyError, TypeError):
            self.warnings += [
                'Could not find sequences for voucher {0} and gene_code {1}'.format(
                    code, gene_code)]
            return '?'
        return this_voucher_seqs

    def create_seq_record(self, sequence_str, gene_code):
        """
        Adds ? if the sequence is not long enough
        :param sequence_str:
        :return: str.
        """
        length = self.gene_codes_metadata[gene_code]['length']
        length_difference = length - len(sequence_str)

        sequence_str += '?' * length_difference
        return sequence_str

    def get_taxon_names_for_taxa(self):
        """Returns dict: {'CP100-10': {'taxon': 'name'}}

        Takes list of voucher_codes and list of taxon_names from cleaned form.

        Returns:
            Dictionary with data, also as dicts.

        """
        vouchers_with_taxon_names = {}

        # TODO: add gene_code. drop it for now
        taxon_names = [i.lower() for i in self.taxon_names]
        if "code" not in taxon_names:
            taxon_names.append("code")
        try:
            taxon_names.remove("genecode")
        except ValueError:
            pass
        all_vouchers = Vouchers.objects.filter(
            code__in=self.voucher_codes,
        ).order_by('code').values(*taxon_names)
        for voucher in all_vouchers:
            code = voucher['code']
            vouchers_with_taxon_names[code] = voucher
        return vouchers_with_taxon_names

    def get_gene_codes_metadata(self):
        """
        :return: dictionary with genecode and base pair number.
        """
        queryset = Genes.objects.all().values(
            'gene_code', 'length', 'reading_frame', 'genetic_code')
        gene_codes_metadata = dict()
        for i in queryset:
            gene_code = i['gene_code']
            gene_codes_metadata[gene_code] = {
                'length': i['length'],
                'reading_frame': i['reading_frame'],
                'genetic_code': i['genetic_code'],
            }
        return gene_codes_metadata
