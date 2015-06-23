from Bio.Seq import Seq

from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command

from create_dataset.utils import CreateDataset
from public_interface.models import Genes


class CreateTNTDatasetTest(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        g1 = Genes.objects.get(gene_code='COI')
        g2 = Genes.objects.get(gene_code='EF1a')
        self.cleaned_data = {
            'gene_codes': [g1, g2],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': None,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'number_genes': None,
            'positions': ['2nd', '3rd'],
            'partition_by_positions': 'ONE',
            'file_format': 'TNT',
            'aminoacids': False,
            'outgroup': '',
        }

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_create_dataset(self):
        expected = 'nstates dna;\nxread\n1523 2\n\n[&dna]\nCP100-10_Melitaea_diamina'
        result = self.dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_create_dataset_outgroup(self):
        cleaned_data = self.cleaned_data
        cleaned_data['outgroup'] = 'CP100-11'
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'nstates dna;\nxread\n1523 2\n\n[&dna]\nCP100-11_Melitaea_diamina'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_create_dataset_ALL_codons(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['ALL']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'nstates dna;\nxread\n2287 2\n\n[&dna]\nCP100-10_Melitaea_diamina'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)

        expected = '?????????????????????????TGAGCCGGTATAATTGGTACATCCCTAAGTCTTATTATTCGAACCGAATTAGGAAATCCTAGTTTTTTAATTGGAGATGATCAAATTTATAATACCATTGTAACAGCTCATGCTTTTATTATAATTTTTTTTATAGTTATGCCAATTATAATTGGAGGATTTGGTAATTGACTTGTACCATTAATATTGGGAGCCCCAGATATAGCTTTCCCCCGAATAAATTATATAAGATTTTGATTATTGCCTCCATCCTTAATTCTTTTAATTTCAAGTAGAATTGTAGAAAATGGGGCAGGAACTGGATGAACAGTTTACCCCCCACTTTCATCTAATATTGCCCATAGAGGAGCTTCAGTGGATTTAGCTATTTTTTCTTTACATTTAGCTGGGATTTCCTCTATCTTAGGAGCTATTAATTTTATTACTACAATTATTAATATACGAATTAATAATATATCTTATGATCAAATACCTTTATTTGTATGAGCAGTAGGAATTACAGCATTACTTCTCTTATTATCTTTACCAGTTTTAGCTGGAGCTATTACTATACTTTTAACGGATCGAAATCTTAATACCTCATTTTTTGATTCCTGCGGAGGAGGAGATCC?????????????????????????????????'
        self.assertTrue(expected in result)

        expected = 'CP100-11_Melitaea_diamina                              ????????????????????????'
        self.assertTrue(expected in result)

    def test_create_dataset_1st_codon(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['1st']
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'nstates dna;\nxread\n762 2\n\n[&dna]\nCP100-10_Melitaea_diamina'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)

        expected = '????????TGGAAGATCACAACAGTGACATTAGGGCATAAAGAGCGTAAATTAGACAAAGGTGATCGCTATGGCGAGTCCAATAATTTTCCTTACTATAAAGGAGGGAGTAGTCCCTTAAGCAGGTGGTGATTTCTGGATTATGGAATAAAAAAACAAAATTGCACTTGTGGGAAGTCCTTTTCGTGGGAAACTAGCACAATTTGTTGGGGC???????????'
        self.assertTrue(expected in result)

    def test_fill_seqs_with_missing_chars(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['ALL']
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = 'CP100-10_Melitaea_diamina                              ???????????????CAAGTCCACCACCACCGGCCACTTGATTTACAAATGTGGTGGTATCGACAAACGTACCATCGAGAAGTTCGAGAAGGAAGCCCAGGAAATGGGCAAGGGTTCCTTCAAGTACGCTTGGGTGTTGGACAAACTTAAGGCTGAGCGCGAGCGTGGTATCACTATTGATATTGCTCTGTGGAAGTTCGAGACTGCCAAATACTATGTAACCATCATCGATGCTCCCGGACACAGAGATTTCATCAAGAACATGATCACCGGAACATCACAAGCCGATTGCGCCGTACTTATCGTCGCCGCCGGTACTGGTGAGTTCGAAGCCGGTATCTCAAAGAACGGTCAGACCCGTGAGCACGCTCTGCTCGCCTTCACATTAGGTGTAAAGCAGCTGATTGTAGGAGTCAACAAAATGGACTCCACTGAGCCCCCATACAATGAGGGACGTTTCGAGGAAATCAAAAAGGAAGTGTCCTCTTACATCAAGAAGATCGGTTACAACCCAGCTGCCGTCGCTTTCGTACCCATTTCTGGCTGGCACGGAGACAACATGCTGGAGCCATCTACCAAAATGTCCCGGTTCAAGGGATGGCAAGTGGAGCGCAAAGAAGGCAAGG???AAGGTAAATGCCTCATTGAAGCTC???ACGCCATCCTTCCTCCGG?????CCCAC????????????????????????????????????????????????TATTGGTACAGTGCCCGTAGGCAGAGTAGAAACTGGTATCCTCAAACCAGGTACCATTGTTGTTTTCGCTCCCGCCAACATCACCACTGAAGTCAAATCTGTGGAGATGCACCACGAAGCTCTCCAAGAGGCTGTACCTGGAGACAATGTAGGTTTCAACGTCAAGAACGTTTCCGTCAAGGAATTACGTCGTGGTTATGTAGCTGGTGACTCCAAGAACAACCCACCCAAGGGAGCTGCTGACTTCACCGCACAAGTCATTGTGCTCAACCACCCCGGTCAAATCTCCAATGGCTACACACCTGTGCTCGATTGCCACACAGCTCACATTGCCTGCAAATTCGCCGAAATCAAAGAAAAGGTTGACCGTCGTTCCGGTAAATCYACTGAGGACAATCCTAAATCTATCAAATCTGGTGATGCTGCCATTGTGAACTTGGTACCTTCCAAACCCCTCTGTGTGGAGGCCTTCCAAGAATTCCCACCTCTTGGTCG????????????'
        self.assertTrue(expected in result)

    def test_drop_gene(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['ALL']
        cleaned_data['number_genes'] = 2
        dataset_creator = CreateDataset(cleaned_data)
        result = dataset_creator.dataset_str
        expected = '2287 1'
        self.assertTrue(expected in result)

    def test_create_dataset_aa(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['ALL']
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)
        expected = 'XXXXXXXXWAGMIGTSLSLIIRTELGNPSFLIGDDQIYNTIVTAHAFIMIFFMVM'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)

        expected = 'xread\n761 2\n'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)

    def test_create_dataset_aa_with_outgroup(self):
        cleaned_data = self.cleaned_data
        cleaned_data['positions'] = ['ALL']
        cleaned_data['outgroup'] = 'CP100-11'
        cleaned_data['aminoacids'] = True
        dataset_creator = CreateDataset(cleaned_data)
        expected = '[&dna]\nCP100-11_Melitaea_diamina                              XSRYNWYIPKSYY'
        result = dataset_creator.dataset_str
        self.assertTrue(expected in result)
