from django.core.management import call_command, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from public_interface.models import Vouchers
from public_interface.models import Sequences
from public_interface.models import FlickrImages
from public_interface.models import LocalImages
from public_interface.models import Primers
from public_interface.models import GeneSets
from public_interface.models import Genes
from public_interface.models import TaxonSets
from public_interface.management.commands import _migrate_db as migrate_script


class TestCustomCommand(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_no_input_file(self):
        args = []
        opts = {'verbosity': 0}
        cmd = 'migrate_db'
        self.assertRaises(CommandError, call_command, cmd, *args, **opts)

    def test_tables_prefix(self):
        args = []
        opts = {'dumpfile': settings.MEDIA_ROOT + 'test_db_dump.xml', 'prefix': 'vosesq_', 'verbosity': 0}
        cmd = 'migrate_db'
        self.assertRaises(ValueError, call_command, cmd, *args, **opts)

    def test_orden_none(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('', b.orden)

    def test_orden_null(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('', b.orden)

    def test_orden_space(self):
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual('', b.orden)

    def test_superfamily(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('Papilionoidea', b.superfamily)

    def test_family(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('Nymphalidae', b.family)

    def test_family_empty(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('', b.family)

    def test_family_space(self):
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual('', b.family)

    def test_subfamily(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('Nymphalinae', b.subfamily)

    def test_subfamily_empty(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('', b.subfamily)

    def test_subfamily_space(self):
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual('', b.subfamily)

    def test_subfamily_null(self):
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual('', b.subfamily)

    def test_tribe_null_with_space(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('', b.tribe)

    def test_genus(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('Melitaea?', b.genus)

    def test_accession(self):
        b = Sequences.objects.get(code='CP100-10', gene__gene_code='EF1a')
        self.assertEqual('AY218269', b.accession)

    def test_max_altitude_null_as_str(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual(None, b.max_altitude)

    def test_max_altitude_null(self):
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual(None, b.max_altitude)

    def test_max_altitude_empty_with_space(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual(None, b.max_altitude)

    def test_max_altitude1(self):
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual(600, b.max_altitude)

    def test_max_altitude2(self):
        b = Vouchers.objects.get(code='CP100-13')
        self.assertEqual(2500, b.max_altitude)

    def test_max_altitude3(self):
        b = Vouchers.objects.get(code='CP100-14')
        self.assertEqual(2000, b.max_altitude)

    def test_voucher_none(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('no voucher', b.voucher)

    def test_voucher_spread(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('spread', b.voucher)

    def test_voucher_unspread(self):
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual('in envelope', b.voucher)

    def test_voucher_null(self):
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual('unknown', b.voucher)

    def test_voucher_empty(self):
        b = Vouchers.objects.get(code='CP100-13')
        self.assertEqual('unknown', b.voucher)

    def test_voucher_photo(self):
        b = Vouchers.objects.get(code='CP100-14')
        self.assertEqual('only photo', b.voucher)

    def test_voucher_lost(self):
        b = Vouchers.objects.get(code='CP100-15')
        self.assertEqual('lost', b.voucher)

    def test_voucher_destroyed(self):
        b = Vouchers.objects.get(code='CP100-16')
        self.assertEqual('destroyed', b.voucher)

    def test_voucher_no_photo(self):
        b = Vouchers.objects.get(code='CP100-17')
        self.assertEqual('in envelope', b.voucher)

    def test_voucher_other(self):
        b = Vouchers.objects.get(code='CP100-17')
        self.assertEqual('in envelope', b.voucher)

    def test_voucher_image(self):
        b = Vouchers.objects.get(code='CP100-09')
        c = FlickrImages.objects.all().filter(voucher=b)
        results = [i.voucher_image for i in c]
        self.assertTrue('https://www.flickr.com/photos/nsg_db/15728978251/' in results)

    def test_voucher_image_none(self):
        b = Vouchers.objects.get(code='CP100-18')
        c = FlickrImages.objects.all().filter(voucher=b)
        results = [i.voucher_image for i in c]
        self.assertEqual([], results)

    def test_country(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('FINLAND', b.country)

    def test_sex1(self):
        result = migrate_script.get_sex('female')
        expected = 'female'
        self.assertEqual(expected, result)

    def test_sex2(self):
        result = migrate_script.get_sex('Female')
        expected = 'female'
        self.assertEqual(expected, result)

    def test_sex3(self):
        result = migrate_script.get_sex('f')
        expected = 'female'
        self.assertEqual(expected, result)

    def test_sex4(self):
        result = migrate_script.get_sex('F')
        expected = 'female'
        self.assertEqual(expected, result)

    def test_sex5(self):
        result = migrate_script.get_sex('Mae')
        expected = 'male'
        self.assertEqual(expected, result)

    def test_sex6(self):
        result = migrate_script.get_sex('male')
        expected = 'male'
        self.assertEqual(expected, result)

    def test_sex7(self):
        result = migrate_script.get_sex('Male')
        expected = 'male'
        self.assertEqual(expected, result)

    def test_sex8(self):
        result = migrate_script.get_sex('m')
        expected = 'male'
        self.assertEqual(expected, result)

    def test_sex9(self):
        result = migrate_script.get_sex('M')
        expected = 'male'
        self.assertEqual(expected, result)

    def test_sex10(self):
        result = migrate_script.get_sex('NA')
        expected = 'unknown'  # unknown
        self.assertEqual(expected, result)

    def test_sex11(self):
        result = migrate_script.get_sex('NULL')
        expected = 'unknown'  # unknown
        self.assertEqual(expected, result)

    def test_sex12(self):
        result = migrate_script.get_sex(None)
        expected = 'unknown'  # unknown
        self.assertEqual(expected, result)

    def test_sex13(self):
        result = migrate_script.get_sex('Worker')
        expected = 'worker'
        self.assertEqual(expected, result)

    def test_sex14(self):
        b = Vouchers.objects.get(code='CP100-09')
        expected = 'female'
        self.assertEqual(expected, b.sex)

    def test_primers(self):
        b = Sequences.objects.get(code='CP100-10', gene__gene_code='EF1a')
        c = Primers.objects.filter(for_sequence=b)

        primers_f = [i.primer_f for i in c]
        self.assertTrue('Cho', primers_f)

    def test_primers_some_none(self):
        b = Sequences.objects.get(code='CP100-10', gene__gene_code='wingless')
        c = Primers.objects.filter(for_sequence=b)

        primers_f = [i.primer_f for i in c]
        self.assertEqual(['lep1'], primers_f)

    def test_geneset_name(self):
        b = GeneSets.objects.get(geneset_name='3genes')
        self.assertEqual(b.geneset_name, '3genes')

    def test_geneset_creator(self):
        b = GeneSets.objects.get(geneset_name='3genes')
        self.assertEqual(b.geneset_creator, 'Niklas')

    def test_geneset_description(self):
        b = GeneSets.objects.get(geneset_name='3genes')
        self.assertEqual(b.geneset_description, '3 standard genes')

    def test_geneset_description_empty(self):
        b = GeneSets.objects.get(geneset_name='2genes')
        self.assertEqual(b.geneset_description, '')

    def test_geneset_list(self):
        b = GeneSets.objects.get(geneset_name='3genes')
        expected = ['COI', 'EF1a', 'wingless']
        self.assertEqual(expected, b.geneset_list.splitlines())

    def test_gene(self):
        b = Genes.objects.get(gene_code='COII')
        expected = None
        self.assertEqual(expected, b.reading_frame)

    def test_taxonset_name(self):
        b = TaxonSets.objects.get(taxonset_name='Erebia')
        self.assertEqual(b.taxonset_name, 'Erebia')

    def test_taxonset_list(self):
        b = TaxonSets.objects.get(taxonset_name='Erebia')
        expected = 'CP100-10\nCP100-11'
        self.assertEqual(expected, b.taxonset_list)

    def test_type_species_dont_know(self):
        value = '0'
        expected = 'unknown'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_yes(self):
        value = '1'
        expected = 'yes'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_no(self):
        value = '2'
        expected = 'not'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_null(self):
        value = None
        expected = 'unknown'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_code_bold(self):
        """Parse bold id, for completeness"""
        expected = 'BCIBT193-09'
        b = Vouchers.objects.get(code='CP100-18')
        self.assertEqual(expected, b.code_bold)

    def test_determined_by(self):
        expected = 'R. Núñez'
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual(expected, b.determined_by)

    def test_determined_by_null(self):
        expected = ''
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual(expected, b.determined_by)

    def test_date_collection(self):
        expected = "1996-03-25"
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual(expected, b.date_collection)

    def test_member_superuser_true(self):
        result = User.objects.get(username='admin').is_superuser
        self.assertTrue(result)

    def test_member_superuser_false(self):
        result = User.objects.get(username='carlosp420').is_superuser
        self.assertFalse(result)

    def test_member_first_name(self):
        expected = 'Carlos'
        result = User.objects.get(username='carlosp420').first_name
        self.assertEqual(expected, result)

    def test_member_last_name(self):
        expected = 'Pena'
        result = User.objects.get(username='carlosp420').last_name
        self.assertEqual(expected, result)

    def test_voucher_image_in_local_folder(self):
        v = Vouchers.objects.get(code='CP100-10')
        expected = {'voucher_image': 'kitten1.jpg'}
        result = LocalImages.objects.filter(voucher=v).values('voucher_image')
        self.assertTrue(expected in result)

        expected = {'voucher_image': 'kitten3.jpg'}
        result = LocalImages.objects.filter(voucher=v).values('voucher_image')
        self.assertTrue(expected in result)

    def test_avoid_importing_null_sequences(self):
        s = Sequences.objects.filter(code='CP100-15')
        expected = 1
        result = len(s)
        self.assertEqual(expected, result)

    def test_avoid_importing_invalid_sequences(self):
        self.assertRaises(Sequences.DoesNotExist,
                          Sequences.objects.get, code='CP100-15', gene__gene_code='COII')

    def test_validate_sequence_true(self):
        sequence = 'ATCAGAN?-'
        validation = migrate_script.validate_sequence(sequence)
        self.assertEqual(validation.is_valid, True)

    def test_validate_sequence_false_whith_space(self):
        sequence = 'ATCAGAN ?-'
        validation = migrate_script.validate_sequence(sequence)
        self.assertEqual(validation.is_valid, False)
        self.assertEqual(validation.invalid_character, 'White space')

    def test_validate_sequence_false_tilde(self):
        sequence = 'ATCAGAN~?-'
        validation = migrate_script.validate_sequence(sequence)
        self.assertEqual(validation.is_valid, False)
        self.assertEqual(validation.invalid_character, '~')

    def test_validate_sequence_false_null(self):
        sequence = None
        validation = migrate_script.validate_sequence(sequence)
        self.assertEqual(validation.is_valid, False)
        self.assertEqual(validation.invalid_character, 'Empty sequence')
