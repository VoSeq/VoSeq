import itertools
import json
import re

from django.conf import settings

from Bio.Seq import Seq

from stats.models import Stats


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
            voucher_codes_clean.append(i_clean.lower())
        else:
            voucher_codes_clean.append(i.lower())
    voucher_codes_set = set(voucher_codes_clean)

    vouchers_to_drop = []
    for i in voucher_codes:
        if re.search('^--', i):
            vouchers_to_drop.append(re.sub('^--', '', i).lower())

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

    gene_codes_lower_case = [i.lower() for i in gene_codes]
    return set(gene_codes_lower_case)


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


def strip_question_marks(seq):
    """Having too many ambiguous characters will mess up DNA translation.

    :returns sequence and number of ambiguous bases removed at start.
    """
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
    return out_clean


def chain_and_flatten(seq1, seq2):
    """Takes seq objects which only contain certain codon positions.

    Combines the two seq objects and returns another seq object.

    """
    out = []
    append = out.append

    my_chain = itertools.zip_longest(seq1, seq2)
    for i in itertools.chain.from_iterable(my_chain):
        if i is not None:
            append(i)

    return Seq(''.join(out))
