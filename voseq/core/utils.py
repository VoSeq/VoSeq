import itertools
import json
import re

from django.conf import settings

from Bio.Seq import Seq
from Bio.Alphabet import IUPAC
from Bio.Alphabet import generic_dna
from Bio.Data.CodonTable import TranslationError

from stats.models import Stats
from . import exceptions


def get_voucher_codes(cleaned_data):
    """Processes list of voucher codes entered by users.

    It receives data from a **Form class** (`cleaned_data`) and makes sure that
    there are not duplicated voucher codes passed to the dataset builder.
    It also drops voucher codes if specified by users using the double dash:
    `--CP100-10`.

    Args:
        * `form.cleaned_data`: taken from a Form class

    Returns:
        set of voucher codes, no dupes, dropped unwanted.
    """
    voucher_codes = []
    if cleaned_data['taxonset'] is not None:
        voucher_codes = json.loads(cleaned_data['taxonset'].taxonset_list)
    if cleaned_data['voucher_codes'] != '':
        voucher_codes += cleaned_data['voucher_codes'].splitlines()

    voucher_codes_clean = []
    for i in voucher_codes:
        if re.search('^--', i):
            i_clean = re.sub('^--', '', i)
            voucher_codes_clean.append(i_clean)
        else:
            voucher_codes_clean.append(i)
    voucher_codes_set = set(voucher_codes_clean)

    vouchers_to_drop = []
    for i in voucher_codes:
        if re.search('^--', i):
            vouchers_to_drop.append(re.sub('^--', '', i))

    voucher_codes_filtered = []
    for i in voucher_codes_set:
        if i not in vouchers_to_drop:
            voucher_codes_filtered.append(i)
    return voucher_codes_filtered


def get_gene_codes(cleaned_data):
    """Processes list of gene codes entered by users.

    It receives data from a **Form class** (`cleaned_data`) and makes sure that
    there are not duplicated gene codes passed to the dataset builder.

    Args:
        * `form.cleaned_data`: taken from a Form class

    Returns:
        set of gene codes, no dupes.
    """
    gene_codes = []
    if cleaned_data['geneset'] is not None:
        gene_codes = json.loads(cleaned_data['geneset'].geneset_list)
    if len(cleaned_data['gene_codes']) > 0:
        gene_codes += [i.gene_code for i in cleaned_data['gene_codes']]

    gene_codes.sort()
    return set(gene_codes)


def get_version_stats():
    """
    Returns version and database statistics for page footer.
    """
    version = settings.VERSION
    try:
        stats = Stats.objects.get(pk=1)
    except Stats.DoesNotExist:
        stats = ''

    return version, stats


def flatten_taxon_names_dict(dictionary):
    """Converts a dict to string suitable for FASTA object id

    Args:
        ``dictionary``: {'code': 'CP100-10', 'orden': 'Lepidoptera'. 'genus': 'Danaus'}

    Returns:
        Flattened as string: 'CP100-10_Lepidoptera_Danaus'

    """
    out = ''
    try:
        out += dictionary['code'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['orden'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['superfamily'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['family'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['subfamily'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['tribe'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['subtribe'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['genus'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['species'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['subspecies'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['author'] + "_"
    except KeyError:
        pass

    try:
        out += dictionary['hostorg'] + "_"
    except KeyError:
        pass

    out_striped = re.sub('_+', '_', out)
    out_clean = re.sub('_$', '', out_striped)
    return out_clean.replace(" ", "_")


def chain_and_flatten(seqs):
    """Takes seq objects which only contain certain codon positions.

    Combines the two seq objects and returns another seq object.

    """
    out = []
    append = out.append

    my_chain = itertools.zip_longest(seqs[0], seqs[1])
    for i in itertools.chain.from_iterable(my_chain):
        if i is not None:
            append(i)

    return Seq(''.join(out))


def get_start_translation_index(gene_model, removed):
    if int(gene_model['reading_frame']) == 1:
        if removed % 3 == 0:
            start_translation = 0
        if removed % 3 == 1:
            start_translation = 2
        if removed % 3 == 2:
            start_translation = 1
    elif int(gene_model['reading_frame']) == 2:
        if removed % 3 == 0:
            start_translation = 1
        if removed % 3 == 1:
            start_translation = 0
        if removed % 3 == 2:
            start_translation = 2
    elif int(gene_model['reading_frame']) == 3:
        if removed % 3 == 0:
            start_translation = 2
        if removed % 3 == 1:
            start_translation = 1
        if removed % 3 == 2:
            start_translation = 0
    else:
        raise exceptions.MissingReadingFrameForGene("Gene %s" % gene_model['gene_code'])
    return start_translation


def translate_to_protein(gene_model, sequence, seq_description, seq_id, file_format=None):
    removed = 0
    if file_format == 'FASTA':
        sequence, removed = strip_question_marks(sequence)
        print(">>>>>>>seqeunce", sequence)
        print(">>>>>>>removed", removed)
    seq_seq = sequence.replace('?', 'N')

    start_translation = get_start_translation_index(gene_model, removed)

    seq_obj = Seq(seq_seq[start_translation:], generic_dna)

    if '---' in seq_seq:  # we have gaps
        try:
            prot_sequence = gapped_translation(seq_obj, gene_model['genetic_code'])
        except TranslationError as e:
            print("Error %s" % e)
            return ""
    else:
        try:
            prot_sequence = seq_obj.translate(table=gene_model['genetic_code'])
        except TranslationError as e:
            print("Error %s" % e)
            return ""

    if file_format == 'PHY':
        return str(prot_sequence)

    out = '>' + seq_id + ' ' + seq_description + '\n'
    out += str(prot_sequence) + '\n'
    # TODO warn when tranlation issues stop codon, voucher code and gene code
    return out


def gapped_translation(seq_obj, genetic_code):
    gap_indexes, sequence = get_gap_indexes(seq_obj)
    seq = Seq(sequence, generic_dna)
    ungapped_seq = seq.ungap('-')
    translated_seq = ungapped_seq.translate(table=genetic_code)
    translated_seq_with_gaps = add_gaps_to_seq(translated_seq, gap_indexes)
    return str(translated_seq_with_gaps)


def add_gaps_to_seq(aa_sequence, gap_indexes):
    aa_seq_as_list = list(aa_sequence)

    number_of_question_marks_appended = 0
    for index in gap_indexes:
        new_index = index - number_of_question_marks_appended
        try:
            this_aa = aa_seq_as_list[new_index]
        except IndexError:
            this_aa = ''

        try:
            aa_seq_as_list[new_index] = '?' + this_aa
        except IndexError:
            aa_seq_as_list.append('?')
        number_of_question_marks_appended += 1
    return ''.join(aa_seq_as_list)


def get_gap_indexes(seq_obj):
    """If - is found not forming gap codons, it will be replaced by ? and
    the new sequence will be returned with this replacemen.
    """
    indexes_for_gaps_in_translated_sequence = []
    new_sequence = ''

    i = 0
    for index in range((len(seq_obj) // 3) + 1):
        j = i + 3
        tmp = str(seq_obj[i:j])
        if tmp.find('---') == 0:
            indexes_for_gaps_in_translated_sequence.append(index)
        elif '-' in tmp:
            tmp = tmp.replace('-', '?')
        new_sequence += tmp
        i += 3
    return indexes_for_gaps_in_translated_sequence, new_sequence


def strip_question_marks(seq):
    removed = 0
    seq = seq.upper()

    res = re.search('^(\?+)', seq)
    if res:
        removed += len(res.groups()[0])
    seq = re.sub('^\?+', '', seq)

    res = re.search('^(N+)', seq)
    if res:
        removed += len(res.groups()[0])
    seq = re.sub('^N+', '', seq)

    seq = re.sub('\?+$', '', seq)
    seq = re.sub('N+$', '', seq)
    return seq, removed
