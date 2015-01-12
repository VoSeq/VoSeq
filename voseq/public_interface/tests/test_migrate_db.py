from django.core.management import call_command
from django.core.management import CommandError
from django.test import TestCase

from public_interface.models import Vouchers
from public_interface.models import Sequences
from public_interface.models import FlickrImages
from public_interface.models import Primers


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
        self.assertEqual('', b.superfamily)

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
        self.assertEqual('n', b.voucher)

    def test_voucher_empty(self):
        b = Vouchers.objects.get(code='CP100-13')
        self.assertEqual('n', b.voucher)

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
