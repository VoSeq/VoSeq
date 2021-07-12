from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.client import Client

from create_dataset.models import Dataset
from create_dataset.tasks import create_dataset
from create_dataset.utils import CreateDataset
from public_interface.models import Genes, Sequences, TaxonSets, GeneSets


class CreateFASTADatasetTest(TestCase):
    def setUp(self):
        with connection.cursor() as cursor:
            cursor.execute("alter sequence public_interface_genes_id_seq restart with 1")
            cursor.execute("alter sequence public_interface_taxonsets_id_seq restart with 1")
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_data.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

        Genes.objects.all().update(genetic_code=1)
        g1 = Genes.objects.get(gene_code='COI-begin')
        g2 = Genes.objects.get(gene_code='ef1a')
        self.cleaned_data = {
            'gene_codes': [g1, g2],
            'taxonset': None,
            'voucher_codes': 'CP100-10\r\nCP100-11',
            'geneset': None,
            'taxon_names': ['CODE', 'GENUS', 'SPECIES'],
            'number_genes': None,
            'translations': False,
            'degen_translations': 'normal',
            'positions': ['ALL'],
            'partition_by_positions': 'by gene',
            'file_format': 'FASTA',
            'aminoacids': True,
            'outgroup': '',
        }

        self.user = User.objects.get(username='admin')
        self.user.set_password('pass')
        self.user.save()

        self.c = Client()
        self.dataset_creator = CreateDataset(self.cleaned_data)
        self.maxDiff = None

    def test_create_dataset__balanced(self):
        """Test that we fill in with question marks the sequence when it is
        lacking for a voucher
        """
        seqs = Sequences.objects.filter(gene__gene_code='ef1a', code__code='CP100-10')
        seqs.delete()
        dataset_obj = Dataset.objects.create()

        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[],
            voucher_codes="",
            file_format='NEXUS',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=False,
            aminoacids=False,
            degen_translations='NORMAL',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        self.assertIn("[ef1a]\nCP100_10_Aus_aus", dataset_obj.content)

    def test_create_dataset__gaps(self):
        """Test that gaps have not been converted to underscores."""
        seq = Sequences.objects.get(code="CP100-10", gene__gene_code="COI-begin")
        this_seq = list(seq.sequences)
        this_seq[-3:] = '---'
        seq.sequences = "".join(this_seq)
        seq.save()

        dataset_obj = Dataset.objects.create()

        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[2],  # COI-begin
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=False,
            aminoacids=False,
            degen_translations='NORMAL',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        self.assertFalse("___" in str(dataset_obj.content))

    def test_create_dataset_degenerated(self):
        dataset_obj = Dataset.objects.create()
        gene = Genes.objects.get(gene_code="RpS2")
        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[gene.id],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=True,
            aminoacids=False,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        expected = 'MGNMGNMGNMGNMGNMGNMGNMGNMG'
        dataset_obj.refresh_from_db()
        self.assertTrue(expected in str(dataset_obj.content))

    def test_create_dataset_degenerated_warning_data_cannot_be_partitioned(self):
        dataset_obj = Dataset.objects.create()
        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[4],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by codon position',
            translations=True,
            aminoacids=False,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        expected = 'Cannot degenerate codons if they go to different partitions'
        self.assertTrue(expected in dataset_obj.errors)

    def test_create_dataset_degenerated_warning_data_cannot_be_of_partial_codons(self):
        dataset_obj = Dataset.objects.create()
        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[4],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='1st',
            partition_by_positions='by gene',
            translations=True,
            aminoacids=False,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        dataset_obj.refresh_from_db()
        expected = 'Cannot degenerate codons if you have not selected all codon positions'
        self.assertTrue(expected in dataset_obj.errors)

    def test_fasta_as_aminoacids(self):
        dataset_obj = Dataset.objects.create()
        gene = Genes.objects.get(gene_code="RpS2")
        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[gene.id],
            voucher_codes='CP100-10',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=True,
            aminoacids=True,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        expected = 'RRRRRRRRRRRRRRRRRRRRRRRRRRR'
        dataset_obj.refresh_from_db()
        self.assertTrue(expected in str(dataset_obj.content))

    def test_fasta_with_seqs_of_different_sizes(self):
        """Test that an error message is shown to the users GUI."""
        seq = Sequences.objects.get(code="CP100-10", gene__gene_code="COI-begin")
        seq.sequences += 'AAAAAAAAAA'
        seq.save()

        dataset_obj = Dataset.objects.create()
        create_dataset(
            taxonset_id=TaxonSets.objects.last().id,
            geneset_id=GeneSets.objects.last().id,
            gene_codes_ids=[2],
            voucher_codes='',
            file_format='FASTA',
            outgroup='',
            positions='ALL',
            partition_by_positions='by gene',
            translations=False,
            aminoacids=False,
            degen_translations='normal',
            special=False,
            taxon_names=['CODE', 'GENUS', 'SPECIES'],
            number_genes='',
            introns='YES',
            dataset_obj_id=dataset_obj.id,
        )
        expected = "Matrix Nchar 4749 does not match data length (4739) for taxon"
        dataset_obj.refresh_from_db()
        self.assertTrue(expected in str(dataset_obj.errors))
