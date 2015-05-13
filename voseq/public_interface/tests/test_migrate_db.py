import json

from django.core.management import call_command
from django.core.management import CommandError
from django.test import TestCase

from public_interface.models import Vouchers
from public_interface.models import Sequences
from public_interface.models import FlickrImages
from public_interface.models import Primers
from public_interface.models import GeneSets
from public_interface.models import TaxonSets
from public_interface.management.commands import _migrate_db as migrate_script


class TestCustomCommand(TestCase):
    def setUp(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'verbosity': 0}
        cmd = 'migrate_db'
        call_command(cmd, *args, **opts)

    def test_no_input_file(self):
        args = []
        opts = {'verbosity': 0}
        cmd = 'migrate_db'
        self.assertRaises(CommandError, call_command, cmd, *args, **opts)

    def test_tables_prefix(self):
        args = []
        opts = {'dumpfile': 'test_db_dump.xml', 'prefix': 'vosesq_', 'verbosity': 0}
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
        b = Sequences.objects.get(code='CP100-10', gene_code='EF1a')
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
        self.assertEqual('n', b.voucher)

    def test_voucher_spread(self):
        b = Vouchers.objects.get(code='CP100-10')
        self.assertEqual('s', b.voucher)

    def test_voucher_unspread(self):
        b = Vouchers.objects.get(code='CP100-11')
        self.assertEqual('e', b.voucher)

    def test_voucher_null(self):
        b = Vouchers.objects.get(code='CP100-12')
        self.assertEqual('u', b.voucher)

    def test_voucher_empty(self):
        b = Vouchers.objects.get(code='CP100-13')
        self.assertEqual('u', b.voucher)

    def test_voucher_photo(self):
        b = Vouchers.objects.get(code='CP100-14')
        self.assertEqual('p', b.voucher)

    def test_voucher_lost(self):
        b = Vouchers.objects.get(code='CP100-15')
        self.assertEqual('l', b.voucher)

    def test_voucher_destroyed(self):
        b = Vouchers.objects.get(code='CP100-16')
        self.assertEqual('d', b.voucher)

    def test_voucher_no_photo(self):
        b = Vouchers.objects.get(code='CP100-17')
        self.assertEqual('e', b.voucher)

    def test_voucher_other(self):
        b = Vouchers.objects.get(code='CP100-17')
        self.assertEqual('e', b.voucher)

    def test_voucher_image(self):
        b = Vouchers.objects.get(code='CP100-09')
        c = FlickrImages.objects.all().filter(voucher=b)
        results = [i.voucherImage for i in c]
        self.assertTrue('https://www.flickr.com/photos/nsg_db/15728978251/' in results)

    def test_country(self):
        b = Vouchers.objects.get(code='CP100-09')
        self.assertEqual('FINLAND', b.country)

    def test_sex1(self):
        result = migrate_script.get_sex('female')
        expected = 'f'
        self.assertEqual(expected, result)

    def test_sex2(self):
        result = migrate_script.get_sex('Female')
        expected = 'f'
        self.assertEqual(expected, result)

    def test_sex3(self):
        result = migrate_script.get_sex('f')
        expected = 'f'
        self.assertEqual(expected, result)

    def test_sex4(self):
        result = migrate_script.get_sex('F')
        expected = 'f'
        self.assertEqual(expected, result)

    def test_sex5(self):
        result = migrate_script.get_sex('Mae')
        expected = 'm'
        self.assertEqual(expected, result)

    def test_sex6(self):
        result = migrate_script.get_sex('male')
        expected = 'm'
        self.assertEqual(expected, result)

    def test_sex7(self):
        result = migrate_script.get_sex('Male')
        expected = 'm'
        self.assertEqual(expected, result)

    def test_sex8(self):
        result = migrate_script.get_sex('m')
        expected = 'm'
        self.assertEqual(expected, result)

    def test_sex9(self):
        result = migrate_script.get_sex('M')
        expected = 'm'
        self.assertEqual(expected, result)

    def test_sex10(self):
        result = migrate_script.get_sex('NA')
        expected = 'u'  # unknown
        self.assertEqual(expected, result)

    def test_sex11(self):
        result = migrate_script.get_sex('NULL')
        expected = 'u'  # unknown
        self.assertEqual(expected, result)

    def test_sex12(self):
        result = migrate_script.get_sex(None)
        expected = 'u'  # unknown
        self.assertEqual(expected, result)

    def test_sex13(self):
        result = migrate_script.get_sex('Worker')
        expected = 'w'
        self.assertEqual(expected, result)

    def test_sex14(self):
        b = Vouchers.objects.get(code='CP100-09')
        expected = 'f'
        self.assertEqual(expected, b.sex)

    def test_primers(self):
        b = Sequences.objects.get(code='CP100-10', gene_code='EF1a')
        c = Primers.objects.filter(for_sequence=b)

        primers_f = [i.primer_f for i in c]
        self.assertTrue('Cho', primers_f)

    def test_primers_some_none(self):
        b = Sequences.objects.get(code='CP100-10', gene_code='wingless')
        c = Primers.objects.filter(for_sequence=b)

        primers_f = [i.primer_f for i in c]
        self.assertEqual(['lep1'], primers_f)

    def test_geneset_name(self):
        b = GeneSets.objects.get(geneset_name='4genes')
        self.assertEqual(b.geneset_name, '4genes')

    def test_geneset_creator(self):
        b = GeneSets.objects.get(geneset_name='4genes')
        self.assertEqual(b.geneset_creator, 'Niklas')

    def test_geneset_description(self):
        b = GeneSets.objects.get(geneset_name='4genes')
        self.assertEqual(b.geneset_description, '4 standard genes')

    def test_geneset_description_empty(self):
        b = GeneSets.objects.get(geneset_name='2genes')
        self.assertEqual(b.geneset_description, '')

    def test_geneset_list(self):
        b = GeneSets.objects.get(geneset_name='4genes')
        expected = ['COI', 'EF1a', 'wingless', '16S']
        self.assertEqual(expected, json.loads(b.geneset_list))

    def test_taxonset_name(self):
        b = TaxonSets.objects.get(taxonset_name='Erebia')
        self.assertEqual(b.taxonset_name, 'Erebia')

    def test_taxonset_list(self):
        b = TaxonSets.objects.get(taxonset_name='Erebia')
        expected = ['CP100-10', 'CP100-11']
        self.assertEqual(expected, json.loads(b.taxonset_list))

    def test_type_species_dont_know(self):
        value = '0'
        expected = 'd'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_yes(self):
        value = '1'
        expected = 'y'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_no(self):
        value = '2'
        expected = 'n'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)

    def test_type_species_null(self):
        value = None
        expected = 'd'
        result = migrate_script.parse_type_species(value)
        self.assertEqual(expected, result)
