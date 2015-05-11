import collections
from collections import namedtuple
import os
import uuid
import re

from core import utils
from public_interface.models import Genes


class Dataset(object):
    """
    Base class to create datasets from Seq objects into FASTA, TNT formats.
    """
    def __init__(self, codon_positions, partition_by_positions, seq_objs, gene_codes,
                 voucher_codes, file_format, outgroup=None, voucher_codes_metadata=None,
                 minimum_number_of_genes=None, aminoacids=None):
        self.minimum_number_of_genes = minimum_number_of_genes
        self.outgroup = outgroup
        self.file_format = file_format
        self.codon_positions = codon_positions
        self.aminoacids = aminoacids
        self.partition_by_positions = partition_by_positions
        # need to sort our seq_objs dictionary by gene_code
        self.seq_objs = collections.OrderedDict(sorted(seq_objs.items(), key=lambda t: t[0]))
        self.gene_codes = gene_codes
        self.gene_code_descriptions = self.get_gene_code_descriptions()
        self.voucher_codes = voucher_codes
        self.vouchers_to_drop = None
        self.number_taxa = len(self.voucher_codes)
        self.reading_frames = self.get_reading_frames()
        self.voucher_codes_metadata = voucher_codes_metadata
        self.warnings = []
        self.partition_list = None

        self.cwd = os.path.dirname(__file__)
        self.guid = self.make_guid()
        self.dataset_file = os.path.join(self.cwd,
                                         'dataset_files',
                                         self.file_format + '_' + self.guid + '.txt',
                                         )
        self.aa_dataset_file = os.path.join(self.cwd,
                                            'dataset_files',
                                            self.file_format + '_aa_' + self.guid + '.txt',
                                            )

    def save_dataset_to_file(self, dataset_str):
        with open(self.dataset_file, 'w') as handle:
            handle.write(dataset_str)

    def save_aa_dataset_to_file(self, aa_dataset_str):
        with open(self.aa_dataset_file, 'w') as handle:
            handle.write(aa_dataset_str)

    def make_guid(self):
        return uuid.uuid4().hex

    def get_gene_for_current_partition(self, gene_models, out,
                                       partitions_incorporated, voucher_code):
        ThisGeneAndPartition = namedtuple('ThisGeneAndPartition', ['this_gene',
                                                                   'this_gene_model',
                                                                   'partitions_incorporated',
                                                                   'out'])
        gene = voucher_code.replace('[', '').replace(']', '').strip()
        ThisGeneAndPartition.this_gene = gene
        ThisGeneAndPartition.this_gene_model = self.get_gene_model_from_gene_id(ThisGeneAndPartition.this_gene, gene_models)
        ThisGeneAndPartition.partitions_incorporated = partitions_incorporated + 1
        if self.file_format == 'NEXUS':
            ThisGeneAndPartition.out = out + ['\n[' + gene + ']']
        else:
            ThisGeneAndPartition.out = out + ['\n']
        return ThisGeneAndPartition

    def get_gene_model_from_gene_id(self, this_gene, gene_models):
        for i in gene_models:
            if i['gene_code'] == this_gene:
                return i

    def get_number_chars_from_partition_list(self, partitions):
        chars = 0
        gene_codes_and_lengths = collections.OrderedDict()

        i = 0
        gene_code = ''
        for item in partitions[0]:
            if item.startswith('\n'):
                if self.file_format == 'NEXUS' or self.file_format == 'PHY':
                    gene_code = item.strip().replace('[', '').replace(']', '')
                    continue
                if self.file_format == 'TNT':
                    gene_code = 'dummy' + str(i)
                    i += 1
                    continue
            if gene_code != '':
                first_entry = re.sub('\s+', ' ', item)
                sequence = first_entry.split(' ')[1]
                chars += len(sequence)
                gene_codes_and_lengths[gene_code] = len(sequence)
                gene_code = ''
        self.gene_codes_and_lengths = gene_codes_and_lengths
        self.number_chars = chars

    def get_number_of_genes_for_taxa(self, partitions):
        number_of_genes_for_taxa = dict()
        vouchers_to_drop = set()

        gene_code = ''
        for item in partitions[0]:
            if item.startswith('\n'):
                if self.file_format == 'NEXUS' or self.file_format == 'PHY':
                    gene_code = item.strip().replace('[', '').replace(']', '')
                    continue
                if self.file_format == 'TNT':
                    gene_code = 'dummy'
                    continue
            if gene_code != '':
                entry = re.sub('\s+', ' ', item)
                voucher, sequence = entry.split(' ')

                if voucher not in number_of_genes_for_taxa:
                    number_of_genes_for_taxa[voucher] = 0

                sequence = sequence.replace('?', '')
                if sequence != '':
                    number_of_genes_for_taxa[voucher] += 1

        if self.minimum_number_of_genes is None:
            self.vouchers_to_drop = []
        else:
            for voucher in number_of_genes_for_taxa:
                if number_of_genes_for_taxa[voucher] < self.minimum_number_of_genes:
                    vouchers_to_drop.add(voucher)
            self.vouchers_to_drop = vouchers_to_drop

    def get_gene_code_descriptions(self):
        gene_metadata = dict()
        genes = Genes.objects.all().values('gene_code', 'description')
        for i in genes:
            gene_code = i['gene_code']
            gene_metadata[gene_code] = i['description']
        return gene_metadata

    def get_reading_frames(self):
        """
        :return: dict of gene_code: reading_frame
        """
        reading_frames = dict()
        genes = Genes.objects.all().values('gene_code', 'reading_frame')
        for gene in genes:
            gene_code = gene['gene_code']
            if gene_code in self.gene_codes:
                reading_frames[gene_code] = gene['reading_frame']
        return reading_frames

    def split_sequence_in_codon_positions(self, gene_code, seq):
        """Puts the sequence in frame, by deleting base pairs at the beginning
        of the sequence if the reading frame is not 1.

        Retuns tuple of nucleotides based on codon positions.

        :param gene_code: as lower case
        :param seq: as BioPython seq object.
        :return: tuple of seq strings.

        Example:
            If reading frame is 2: ATGGGG becomes TGGGG. Then the sequence is
            processed to extract the codon positions requested by the user.

        """
        reading_frame = int(self.reading_frames[gene_code]) - 1
        seq = seq[reading_frame:]

        # This is the BioPython way to get codon positions
        # http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc19
        first_position = seq[0::3]
        second_position = seq[1::3]
        third_position = seq[2::3]
        return first_position, second_position, third_position

    def convert_lists_to_dataset(self, partitions):
        """
        Method to override in order to add headers and footers depending
        on needed dataset.
        """
        out = ''
        for i in partitions:
            out += '\n'
            out += '\n'.join(i)
        dataset_str = out.strip()
        self.save_dataset_to_file(dataset_str)
        return dataset_str

    def translate_this_sequence(self, sequence, this_gene_model, voucher_code):
        aa_sequence = ''
        if this_gene_model['genetic_code'] is None or this_gene_model['reading_frame'] is None:
            self.warnings.append(
                "Cannot translate gene %s sequences into aminoacids."
                " You need to define reading_frame and/or genetic_code." %
                this_gene_model['gene_code'])
        else:
            aa_sequence, warning = utils.translate_to_protein(this_gene_model,
                                                              sequence, '',
                                                              voucher_code,
                                                              self.file_format)
            if warning != '':
                self.warnings.append(warning)
        sequence = aa_sequence

        if sequence == '':
            sequence = '?'
        return sequence

    def get_codons_in_each_partition(self, codons):
        partition_list = ()
        codon_descriptions = []
        codon_pos = []
        for i in codons:
            partition_list += ([],)
            if i == '1st':
                codon_descriptions.append('_1st_codon')
                codon_pos.append(0)
            if i == '2nd':
                codon_descriptions.append('_2nd_codon')
                codon_pos.append(1)
            if i == '3rd':
                codon_descriptions.append('_3rd_codon')
                codon_pos.append(2)
        for gene_code in self.seq_objs:
            this_gene = None

            for seq_record in self.seq_objs[gene_code]:
                if self.reading_frames[gene_code] is None:
                    self.warnings.append("Reading frame for gene %s hasn't been specified so "
                                         "it cannot be included in your dataset." % gene_code)
                    continue

                if this_gene is None:
                    this_gene = seq_record.name

                    for i in range(len(codon_descriptions)):
                        seq_str = self.get_gene_divisor(this_gene, codon_descriptions[i])
                        partition_list[i].append(seq_str)

                codons = self.split_sequence_in_codon_positions(this_gene,
                                                                seq_record.seq)
                for i in range(len(codon_pos)):
                    seq_str = self.format_record_id_and_seq_for_dataset(seq_record.id, codons[codon_pos[i]])
                    partition_list[i].append(seq_str)
        return partition_list

    def get_gene_divisor(self, this_gene, codon_description=None):
        if self.file_format == 'FASTA':
            seq_str = '>' + this_gene
            if codon_description is not None:
                seq_str += codon_description
            seq_str += '\n' + '--------------------'

        if self.file_format == 'GenbankFASTA':
            seq_str = '\n[%s]' % this_gene

        if self.file_format == 'PHY':
            seq_str = '\n[%s]' % this_gene

        if self.file_format == 'TNT':
            seq_str = '\n[%s]' % this_gene

        if self.file_format == 'NEXUS':
            seq_str = '\n[%s]' % this_gene
        return seq_str

    def format_record_id_and_seq_for_dataset(self, seq_record_id, seq_record_seq):
        if self.file_format == 'GenbankFASTA':
            seq_record_id = seq_record_id.split(' ')
            code = seq_record_id[0]
            gene = seq_record_id[1]
            taxon = seq_record_id[2].replace('_', ' ')
            gene_description = self.gene_code_descriptions[gene]

            seq_str = '>' + code + '_' + gene + ' ' + '[organism=' + taxon + '] [specimen-voucher=' + code + '] ' + taxon
            seq_str += ' ' + gene_description + '\n' + str(seq_record_seq)
        if self.file_format == 'FASTA':
            seq_str = '>' + seq_record_id + '\n' + str(seq_record_seq)
        if self.file_format == 'NEXUS' or \
                self.file_format == 'PHY' or \
                self.file_format == 'TNT':
            seq_str = str(seq_record_id).ljust(55) + str(seq_record_seq)
        return seq_str

    def get_codons_in_one_partition(self, codons):
        partition_list = ([],)
        codon_pos = []
        for i in codons:
            if i == '1st':
                codon_pos.append(0)
            if i == '2nd':
                codon_pos.append(1)
            if i == '3rd':
                codon_pos.append(2)
        for gene_code in self.seq_objs:
            this_gene = None

            for seq_record in self.seq_objs[gene_code]:
                if self.reading_frames[gene_code] is None:
                    self.warnings.append("Reading frame for gene %s hasn't been specified so "
                                         "it cannot be included in your dataset." % gene_code)
                    continue

                if this_gene is None:
                    this_gene = seq_record.name

                    gene_divisor = self.get_gene_divisor(this_gene)
                    partition_list[0].append(gene_divisor)

                codons = self.split_sequence_in_codon_positions(this_gene,
                                                                seq_record.seq)

                codon_seqs = str(utils.chain_and_flatten([codons[i] for i in codon_pos]))
                seq_str = self.format_record_id_and_seq_for_dataset(seq_record.id, codon_seqs)

                partition_list[0].append(seq_str)
        self.partition_list = partition_list
        return partition_list

    def from_seq_objs_to_dataset(self):
        """Take a list of BioPython's sequence objects and return a FASTA string

        Returns:
            The FASTA string will contain the gene_code at the top as if it were
            another FASTA gene sequence.

        """
        if '1st' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'ALL' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'ALL' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['2nd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['2nd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '2nd' in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'ALL' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st', '2nd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '2nd' in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                'ALL' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_one_partition(['1st', '2nd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '3rd' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '3rd' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '3rd' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_one_partition(['1st', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['2nd', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                'ONE' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_one_partition(['2nd', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['2nd', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if ('ALL' in self.codon_positions or
                ('1st' in self.codon_positions and '2nd' in self.codon_positions and '3rd' in self.codon_positions)) \
                and 'EACH' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st', '2nd', '3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if ('ALL' in self.codon_positions or
                ('1st' in self.codon_positions and '2nd' in self.codon_positions and '3rd' in self.codon_positions)) \
                and 'ONE' in self.partition_by_positions:
            self.partition_list = ([],)
            for gene_code in self.seq_objs:
                this_gene = None
                for seq_record in self.seq_objs[gene_code]:
                    if this_gene is None:
                        this_gene = seq_record.name

                        seq_str = self.get_gene_divisor(this_gene)
                        self.partition_list[0].append(seq_str)

                    if self.file_format == 'GenbankFASTA':
                        seq_str = self.format_record_id_and_seq_for_dataset(seq_record.description + ' ' +
                                                                            this_gene + ' ' +
                                                                            seq_record.id.replace(seq_record.description + '_', ''), seq_record.seq)
                    else:
                        seq_str = self.format_record_id_and_seq_for_dataset(seq_record.id, seq_record.seq)
                    self.partition_list[0].append(seq_str)
            return self.convert_lists_to_dataset(self.partition_list)

        if 'ALL' in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = ([], [],)

            for gene_code in self.seq_objs:
                if self.reading_frames[gene_code] is None:
                    self.warnings.append("Reading frame for gene %s hasn't been specified so "
                                         "it cannot be included in your dataset." % gene_code)
                    continue

                this_gene = None
                for seq_record in self.seq_objs[gene_code]:
                    if this_gene is None:
                        this_gene = seq_record.name

                        seq_str = '>' + this_gene + '_1st_2nd_codons\n' + '--------------------'
                        self.partition_list[0].append(seq_str)

                        seq_str = '>' + this_gene + '_3rd_codon\n' + '--------------------'
                        self.partition_list[1].append(seq_str)

                    codons = self.split_sequence_in_codon_positions(this_gene, seq_record.seq)

                    seq_str = '>' + seq_record.id + '\n' + str(utils.chain_and_flatten([codons[0], codons[1]]))
                    self.partition_list[0].append(seq_str)

                    seq_str = '>' + seq_record.id + '\n' + str(codons[2])
                    self.partition_list[1].append(seq_str)
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['1st'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '2nd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['2nd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '3rd' in self.codon_positions and \
                '1st' not in self.codon_positions and \
                '2nd' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = self.get_codons_in_each_partition(['3rd'])
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '2nd' in self.codon_positions and \
                '3rd' not in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = ([],)
            for gene_code in self.seq_objs:
                this_gene = None
                for seq_record in self.seq_objs[gene_code]:
                    if self.reading_frames[gene_code] is None:
                        self.warnings.append("Reading frame for gene %s hasn't been specified so "
                                             "it cannot be included in your dataset." % gene_code)
                        continue

                    if this_gene is None:
                        this_gene = seq_record.name

                        seq_str = '>' + this_gene + '_1st_2nd_codons\n' + '--------------------'
                        self.partition_list[0].append(seq_str)

                    codons = self.split_sequence_in_codon_positions(this_gene, seq_record.seq)

                    seq_str = '>' + seq_record.id + '\n' + str(utils.chain_and_flatten([codons[0], codons[1]]))
                    self.partition_list[0].append(seq_str)
            return self.convert_lists_to_dataset(self.partition_list)

        if '1st' in self.codon_positions and '2nd' in self.codon_positions and \
                '3rd' in self.codon_positions and \
                '1st2nd_3rd' in self.partition_by_positions:
            self.partition_list = ([], [],)
            for gene_code in self.seq_objs:
                this_gene = None
                for seq_record in self.seq_objs[gene_code]:
                    if self.reading_frames[gene_code] is None:
                        self.warnings.append("Reading frame for gene %s hasn't been specified so "
                                             "it cannot be included in your dataset." % gene_code)
                        continue

                    if this_gene is None:
                        this_gene = seq_record.name

                        seq_str = '>' + this_gene + '_1st_2nd_codons\n' + '--------------------'
                        self.partition_list[0].append(seq_str)

                        seq_str = '>' + this_gene + '_3rd_codon\n' + '--------------------'
                        self.partition_list[1].append(seq_str)

                    codons = self.split_sequence_in_codon_positions(this_gene, seq_record.seq)

                    seq_str = '>' + seq_record.id + '\n' + str(utils.chain_and_flatten([codons[0], codons[1]]))
                    self.partition_list[0].append(seq_str)

                    seq_str = '>' + seq_record.id + '\n' + str(codons[2])
                    self.partition_list[1].append(seq_str)
            return self.convert_lists_to_dataset(self.partition_list)


class CreateFasta(Dataset):
    pass


class CreateGenbankFasta(Dataset):
    def convert_lists_to_dataset(self, partitions):
        """
        Overriden method from base clase in order to add headers and footers depending
        on needed dataset.
        """
        self.get_number_of_genes_for_taxa(partitions)
        self.get_number_chars_from_partition_list(partitions)

        out = []
        aa_out = []

        gene_models = Genes.objects.all().values()

        partitions_incorporated = 0
        for partition in partitions:
            for i in partition:
                i = i.strip()
                if i.startswith('['):
                    this_gene = i.replace('[', '').replace(']', '').strip()
                    this_gene_model = self.get_gene_model_from_gene_id(this_gene, gene_models)
                    partitions_incorporated += 1
                    out += ['\n']
                elif i.startswith('>'):
                    try:
                        voucher_code = re.search('specimen-voucher=(.+)]', i).groups()[0]
                    except AttributeError:
                        continue

                    if voucher_code not in self.vouchers_to_drop:
                        line = i.split('\n')
                        if len(line) > 1:
                            sequence = line[-1]

                            if this_gene_model['genetic_code'] is None or this_gene_model['reading_frame'] is None:
                                self.warnings.append("Cannot translate gene %s sequences into aminoacids."
                                                     " You need to define reading_frame and/or genetic_code." % this_gene_model['gene_code'])
                                continue
                            else:
                                aa_sequence, warning = utils.translate_to_protein(this_gene_model, sequence, '', voucher_code, self.file_format)
                                if warning != '':
                                    self.warnings.append(warning)

                            if aa_sequence.strip() == '':
                                self.warnings.append("Sequence for %s %s was empty" % (voucher_code, this_gene))

                            sequence = utils.strip_question_marks(sequence)[0]
                            out += [line[0] + '\n' + sequence.replace('?', 'N') + '\n']
                            aa_out += [line[0] + '\n' + aa_sequence + '\n']

        dataset_str = ''.join(out)
        aa_dataset_str = ''.join(aa_out)
        self.save_dataset_to_file(dataset_str)
        self.save_aa_dataset_to_file(aa_dataset_str)
        return dataset_str, aa_dataset_str


class CreatePhylip(Dataset):
    def get_charset_block(self, gene_codes_and_lengths):
        charset_block = []

        bp_count_start = 0
        bp_count_end = 0
        self.gene_codes.sort()
        for gene in gene_codes_and_lengths:
            bp_count_end += gene_codes_and_lengths[gene]
            line = 'DNA, ' + gene + ' = ' + str(
                bp_count_start + 1) + '-' + str(bp_count_end)
            bp_count_start += gene_codes_and_lengths[gene]
            charset_block.append(line)
        self.charset_block = "\n".join(charset_block)

    def convert_lists_to_dataset(self, partitions):
        """
        Overriden method from base clase in order to add headers and footers depending
        on needed dataset.
        """
        self.get_number_of_genes_for_taxa(partitions)
        self.get_number_chars_from_partition_list(partitions)
        out = []

        gene_models = Genes.objects.all().values()

        gene_codes_and_lengths = dict()

        partitions_incorporated = 0
        for partition in partitions:
            for i in partition:
                voucher_code = i.split(' ')[0]
                if voucher_code.startswith('\n'):
                    ThisGeneAndPartition = self.get_gene_for_current_partition(
                        gene_models, out, partitions_incorporated, voucher_code
                    )
                    partitions_incorporated = ThisGeneAndPartition.partitions_incorporated
                    out = ThisGeneAndPartition.out
                elif voucher_code not in self.vouchers_to_drop:
                    line = i.split(' ')
                    if len(line) > 1:
                        sequence = line[-1]

                        if self.aminoacids is True:
                            sequence = self.translate_this_sequence(
                                sequence,
                                ThisGeneAndPartition.this_gene_model,
                                voucher_code
                            )

                        gene_codes_and_lengths[ThisGeneAndPartition.this_gene] = len(sequence)

                        if partitions_incorporated == 1:
                            out += [line[0].ljust(55, ' ') + sequence + '\n']
                        else:
                            out += [' ' * 55 + sequence + '\n']

        number_chars = 0
        for k in gene_codes_and_lengths.keys():
            number_chars += gene_codes_and_lengths[k]

        header = [
            str(self.number_taxa - len(self.vouchers_to_drop)) + ' ' + str(number_chars),
        ]

        out = header + out

        self.get_charset_block(gene_codes_and_lengths)
        dataset_str = ''.join(out)
        self.save_dataset_to_file(dataset_str)
        return dataset_str


class CreateTNT(Dataset):
    def convert_lists_to_dataset(self, partitions):
        """
        Overriden method from base clase in order to add headers and footers depending
        on needed dataset.
        """
        self.get_number_of_genes_for_taxa(partitions)
        self.get_number_chars_from_partition_list(partitions)

        gene_models = Genes.objects.all().values()
        gene_codes_and_lengths = collections.OrderedDict()

        out = []

        outgroup_sequences = []
        for partition in partitions:
            for i in partition:
                voucher = i.split(' ')[0]
                if voucher not in self.vouchers_to_drop:
                    if self.outgroup in voucher:
                        outgroup_sequences.append(i)
                        continue

        partitions_incorporated = 0
        partition_count = 0
        for partition in partitions:
            for i in partition:
                voucher_code = i.split(' ')[0]
                if voucher_code.startswith('\n'):
                    ThisGeneAndPartition = self.get_gene_for_current_partition(
                        gene_models, out, partitions_incorporated, voucher_code
                    )
                    out += ['\n[&dna]']
                    if self.outgroup != '':
                        line = outgroup_sequences[partition_count]
                        tmp_line = line.split(' ')
                        sequence = tmp_line[-1]

                        if self.aminoacids is True:
                            sequence = self.translate_this_sequence(
                                sequence,
                                ThisGeneAndPartition.this_gene_model,
                                voucher_code
                            )
                            out += [tmp_line[0].ljust(55, ' ') + sequence]
                        else:
                            out += [outgroup_sequences[partition_count]]
                        partition_count += 1
                elif voucher_code not in self.vouchers_to_drop:
                    line = i.split(' ')
                    if len(line) > 1:
                        sequence = line[-1]

                        if self.aminoacids is True:
                            sequence = self.translate_this_sequence(
                                sequence,
                                ThisGeneAndPartition.this_gene_model,
                                voucher_code
                            )

                    gene_codes_and_lengths[ThisGeneAndPartition.this_gene] = len(sequence)

                    if self.outgroup != '' and self.outgroup not in voucher_code:
                        out += [line[0].ljust(55, ' ') + sequence]
                    elif self.outgroup == '':
                        out += [line[0].ljust(55, ' ') + sequence]

        out += ['\n;\nproc/;']

        number_chars = 0
        for k in gene_codes_and_lengths.keys():
            number_chars += gene_codes_and_lengths[k]

        header = ['nstates dna;\nxread']
        header += [str(number_chars) + ' ' + str(self.number_taxa - len(self.vouchers_to_drop))]

        out = header + out
        dataset_str = '\n'.join(out)
        self.save_dataset_to_file(dataset_str)
        return dataset_str


class CreateNEXUS(Dataset):
    def get_charset_block(self):
        charset_block = []

        bp_count_start = 0
        bp_count_end = 0
        self.gene_codes.sort()
        for gene in self.gene_codes_and_lengths:
            bp_count_end += self.gene_codes_and_lengths[gene]
            line = '    charset ' + gene + ' = ' + str(
                bp_count_start + 1) + '-' + str(bp_count_end) + ';'
            bp_count_start += self.gene_codes_and_lengths[gene]
            charset_block.append(line)
        return charset_block

    def get_partitions_block(self):
        line = 'partition GENES = ' + str(len(self.gene_codes_and_lengths))
        line += ': ' + ', '.join([i for i in self.gene_codes_and_lengths]) + ';\n'
        line += '\nset partition = GENES;\n'
        return [line]

    def get_final_block(self):
        block = "set autoclose=yes;"
        if self.outgroup != '':
            block += '\noutgroup ' + self.voucher_codes_metadata[self.outgroup] + ";"
        block += """
prset applyto=(all) ratepr=variable brlensp=unconstrained:Exp(100.0) shapepr=exp(1.0) tratiopr=beta(2.0,1.0);
lset applyto=(all) nst=mixed rates=gamma [invgamma];
unlink statefreq=(all);
unlink shape=(all) revmat=(all) tratio=(all) [pinvar=(all)];
mcmc ngen=10000000 printfreq=1000 samplefreq=1000 nchains=4 nruns=2 savebrlens=yes [temp=0.11];
 sump relburnin=yes [no] burninfrac=0.25 [2500];
 sumt relburnin=yes [no] burninfrac=0.25 [2500] contype=halfcompat [allcompat];
END;
"""
        return [block.strip()]

    def convert_lists_to_dataset(self, partitions):
        """
        Overriden method from base clase in order to add headers and footers depending
        on needed dataset.
        """
        self.get_number_of_genes_for_taxa(partitions)
        self.get_number_chars_from_partition_list(partitions)

        gene_models = Genes.objects.all().values()
        gene_codes_and_lengths = collections.OrderedDict()

        partitions_incorporated = 0

        out = []

        for partition in partitions:
            for i in partition:
                voucher_code = i.split(' ')[0]
                if voucher_code.startswith('\n'):
                    ThisGeneAndPartition = self.get_gene_for_current_partition(
                        gene_models, out, partitions_incorporated, voucher_code
                    )
                    out = ThisGeneAndPartition.out
                elif voucher_code not in self.vouchers_to_drop:
                    line = i.split(' ')
                    if len(line) > 1:
                        sequence = line[-1]

                        if self.aminoacids is True:
                            sequence = self.translate_this_sequence(
                                sequence,
                                ThisGeneAndPartition.this_gene_model,
                                voucher_code
                            )

                    gene_codes_and_lengths[ThisGeneAndPartition.this_gene] = len(sequence)

                    out += [line[0].ljust(55, ' ') + sequence]

        number_chars = 0
        for k in gene_codes_and_lengths.keys():
            number_chars += gene_codes_and_lengths[k]

        header = [
            '#NEXUS\n',
            'BEGIN DATA;',
            'DIMENSIONS NTAX=' + str(self.number_taxa - len(self.vouchers_to_drop)) + ' NCHAR=' + str(number_chars) + ';',
            'FORMAT INTERLEAVE DATATYPE=DNA MISSING=? GAP=-;',
            'MATRIX',
        ]

        if self.aminoacids is True:
            self.gene_codes_and_lengths = gene_codes_and_lengths

        out = header + out

        out += [';\nEND;']
        out += ['\nbegin mrbayes;']
        out += self.get_charset_block()
        out += self.get_partitions_block()
        out += self.get_final_block()
        dataset_str = '\n'.join(out)
        self.save_dataset_to_file(dataset_str)
        return dataset_str
