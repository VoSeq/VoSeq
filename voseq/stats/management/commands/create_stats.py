from django.conf import settings
from django.core.management.base import BaseCommand

from overview_table.models import OverviewTable
from overview_table.utils import OverviewTableMaker
from public_interface.models import Vouchers
from public_interface.models import Sequences
from stats.models import Stats
from stats.models import VouchersPerGene


class Command(BaseCommand):
    help = 'Extracts total number of orders, families, genera, etc. from ' \
           'our database. Also counts the number of vouchers for each of ' \
           'our genes.\n' \
           'Updates the overview table with the sequence lengths for each gene.'

    def handle(self, *args, **options):
        self.count_vouchers_per_gene()

        queryset = Vouchers.objects.all()

        orders = set()
        families = set()
        genera = set()
        species = set()

        for i in queryset:
            order = i.orden
            family = i.family
            genus = i.genus
            this_species = i.genus + ' ' + i.species

            if order != '':
                orders.add(order)
            if family != '':
                families.add(family)
            if genus != '':
                genera.add(genus)
            if this_species != '':
                species.add(this_species)

        num_vouchers = len(queryset)
        num_orders = len(orders)
        num_families = len(families)
        num_genera = len(genera)
        num_species = len(species)

        queryset = Sequences.objects.all()
        num_sequences = len(queryset)

        Stats.objects.update_or_create(
            id=1,
            defaults={
                'vouchers': num_vouchers,
                'orders': num_orders,
                'families': num_families,
                'genera': num_genera,
                'species': num_species,
                'sequences': num_sequences,
            }
        )

        if 'overview_table' in settings.INSTALLED_APPS:
            self.make_overview_database_table()

    def count_vouchers_per_gene(self):
        genes = Sequences.objects.all().values('gene_code').distinct()

        model_objects = []

        pk_index = 1
        for gene in genes:
            voucher_count = Sequences.objects.filter(gene_code=gene['gene_code']).count()
            gene['voucher_count'] = voucher_count
            model_objects.append(VouchersPerGene(id=pk_index, **gene))
            pk_index += 1

        VouchersPerGene.objects.all().delete()
        VouchersPerGene.objects.bulk_create(model_objects)

    def make_overview_database_table(self):
        o = OverviewTable.objects.all()
        o.delete()

        table = OverviewTableMaker()
        overview_table_items = table.items

        objects_to_upload = []
        for i in overview_table_items:
            i['o_code'] = i['code']
            del i['code']
            o = OverviewTable(**i)
            objects_to_upload.append(o)

        OverviewTable.objects.bulk_create(objects_to_upload)
