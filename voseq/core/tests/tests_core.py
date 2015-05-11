from django.test import TestCase
from django.core.management import call_command

from Bio.Seq import Seq
from Bio.Alphabet import generic_dna

from core import utils
from public_interface.models import Genes
from public_interface.models import Sequences


class TestCore(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_translation_to_protein(self):
        gene_model = Genes.objects.filter(gene_code='COI').values()[0]
        sequence_model = Sequences.objects.get(gene_code='COI', code='CP100-10')
        seq_description = 'seq_description'
        seq_id = 'seq_id'
        expected = "XXXXXXXXWAGMIGTSLS"
        results, warning = utils.translate_to_protein(gene_model, sequence_model.sequences,
                                                      seq_description, seq_id)
        self.assertTrue(expected in results)

    def test_translation_to_protein_invalid_codons(self):
        """Catch exceptions when input has invalid codons due to ?"""
        gene_model = Genes.objects.filter(gene_code='COI').values()[0]
        sequence_model = Sequences.objects.get(gene_code='COI', code='CP100-10')
        seq = sequence_model.sequences
        new_seq = []
        count = 1
        for i in seq:
            if count % 10 == 0:
                i = '?'
            new_seq.append(i)
            count += 1
        sequence_model.sequences = ''.join(new_seq)
        seq_description = 'seq_description'
        seq_id = 'seq_id'
        expected = 'GMXGTSXSLXIRTELGXPSXLIGDDQXYNXIVTAHAXIMXFF'
        results, warning = utils.translate_to_protein(gene_model, sequence_model.sequences,
                                                      seq_description, seq_id)
        self.assertTrue(expected in results)

    def test_translate_to_protein_missing_with_nucleotides(self):
        gene_model = {'genetic_code': 5, 'reading_frame': 1}
        sequence = '?TTCGAAAAATACATCCTATTATTAAAATTATTAATAATTCATTAATTGATCTACCTACCCCATCAAATATTTCATCTTGATGAAATTTTGGATCTTTATTAGGATTATGTTTAATTATTCAAATCATTACTGGGTTATTTTTAACTATACATTATTCAGCTAATATTGATCTAGCTTTTTATAGAGTAAATCATATTTGTCGAAATGTAAATTATGGGTGATTAATTCGAACATTACATGCAAATGGTGCTTCATTTTTTTTTATTTGTATTTATATACATATTGGACGAGGTATTTATTATGAATCTTTTCTATATAAATATACTTGAATAGTTGGAGTATTAATTTTATTCCTATTAATAGCAACAGCTTTTATAGGATATGTTCTACCTTGAGGACAAATATCTTTTTGAGGAGCAACTGTTATTACTAATTTATTATCAGCAATTCCTTATTTAGGTTCTATATTAGTTAACTGAATTTGAGGGGGATTTGCTGTAGATAATGCAACATTAACTCGATTTTATACTTTTCATTTTTTATTACCATTTATTTTAGCAATAATAACTATAATTCATTTATTATTTTTACATCAATATGGATCAAATAACCCATTAGGAATTAATAGAAACCTAGATAAAATTCCTTTTCATCCTTATTTTTCATTTAAAGATTTATTTGGATTTATTATTATATTAATAATTTTAA---TATTAACATTATGAAATCCATATATTTTAGGAGATCCTGATAATTTTATTCCAGCAAATCCTTTAGTAACCCCAATTCATATTCAACCAGAATGATATTTTTTATTTGCTTATGCAATTTTACGATCAATCCCTAATAAATTAGGGGGTGTAATTGCATTAATTATATCTATTGCTATCTTATTTATTTTACCATTTACTTTTAATAAAAAAATTCAAGGAAATCAATTTTATCCTATTAATAAAATTTTATTTTGAAATATAATTATTATTATTATTTTATTAACATGAATTGGCGCTCGTCCAGTTGAAGATCCTTATATTATTACAGGACAAATTCTAACTATTTTATATTTTATATATTATATTTTAACCCCAATCTTTAGAATTTTATGAGATAAA'
        expected = 'XRKMHPIIKIINNSLIDLPTPSNISSWWNFGSLLGLCLIIQIITGLFLTMHYSANIDLAFYSVNHICRNVNYGWLIRTLHANGASFFFICIYMHIGRGIYYESFLYKYTWMVGVLILFLLMATAFMGYVLPWGQMSFWGATVITNLLSAIPYLGSMLVNWIWGGFAVDNATLTRFYTFHFLLPFILAMMTMIHLLFLHQYGSNNPLGINSNLDKIPFHPYFSFKDLFGFIIMLMILXXLTLWNPYILGDPDNFIPANPLVTPIHIQPEWYFLFAYAILRSIPNKLGGVIALIMSIAILFILPFTFNKKIQGNQFYPINKILFWNMIIIIILLTWIGARPVEDPYIITGQILTILYFMYYILTPIFSILWDK'
        result = utils.translate_to_protein(gene_model, sequence, '', '')
        self.assertEqual(expected, result[0])

    def test_flatten_taxon_names_dict(self):
        dictionary = {'code': 'CP100-10', 'orden': 'Lepidoptera',
                      'genus': 'Danaus', 'species': 'sp. 5'}
        expected = 'CP100-10_Lepidoptera_Danaus_sp._5'
        results = utils.flatten_taxon_names_dict(dictionary)
        self.assertEqual(expected, results)

    def test_gapped_translation(self):
        sequence = 'ATG---GCCATTGTAATGGGCCGG'
        expected = 'M?AIVMGR'
        genetic_code = 1
        result = utils.gapped_translation(sequence, genetic_code)
        self.assertEqual(expected, result)

    def test_getting_gap_indexes1(self):
        sequence = 'ATG---GCCATTGTAATGGGCCGG'
        expected = [1]
        indexes, sequence = utils.get_gap_indexes(sequence)
        self.assertEqual(expected, indexes)

    def test_getting_gap_indexes2(self):
        sequence = 'ATG---GCCATT---GTAATGGGCCGG'
        expected = [1, 4]
        indexes, sequence = utils.get_gap_indexes(sequence)
        self.assertEqual(expected, indexes)

    def test_getting_gap_indexes3(self):
        sequence = 'ATG---GCC-TTGTAATGGGCCGG'
        expected = 'ATG---GCC?TTGTAATGGGCCGG'
        indexes, sequence = utils.get_gap_indexes(sequence)
        self.assertEqual(expected, sequence)

    def test_add_gaps_to_seq1(self):
        gap_indexes = [1]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'M?AIVMGR'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq2(self):
        gap_indexes = [1, 4]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'M?AI?VMGR'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq3(self):
        gap_indexes = [1, 5]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'M?AIV?MGR'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq4(self):
        gap_indexes = [2, 5]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'MA?IV?MGR'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq5(self):
        gap_indexes = [2, 5, 7]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'MA?IV?M?GR'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq6(self):
        gap_indexes = [2, 5, 7, 9, 10]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'MA?IV?M?G??R'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq7(self):
        gap_indexes = [0, 5, 7, 9, 10]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = '?MAIV?M?G??R'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))

    def test_add_gaps_to_seq8(self):
        """When the gap is at the end of sequence"""
        gap_indexes = [2, 8]
        sequence = 'ATGGCCATTGTAATGGGCCGG'
        seq = Seq(sequence, generic_dna).translate()
        expected = 'MA?IVMGR?'
        result = utils.add_gaps_to_seq(seq, gap_indexes)
        self.assertEqual(expected, str(result))
