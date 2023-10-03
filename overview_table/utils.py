from public_interface.models import Genes
from public_interface.models import Sequences
from public_interface.models import Vouchers


class OverviewTableMaker(object):
    def __init__(self):
        self.genes = Genes.objects.all().order_by('gene_code').values('gene_code')
        self.items = self.get_vouchers_with_sequences()

    def get_vouchers_with_sequences(self):
        unique_vouchers = self.get_unique()
        sequences = Sequences.objects.all().values('code', 'gene_id', 'total_number_bp')
        sequences = self.convert_to_dict(sequences)

        for voucher in unique_vouchers:
            code = voucher['code']
            voucher['sequence_string'] = self.build_sequence_string(sequences[code])

        return unique_vouchers

    def get_unique(self):
        v = Vouchers.objects.all().filter(sequences__code__isnull=False).values('code', 'orden', 'superfamily', 'family',
                                                                                'subfamily', 'genus', 'species').distinct()
        return v

    def convert_to_dict(self, sequences):
        new_seqs = {}
        for i in sequences:
            gene_id = i['gene_id']
            gene = Genes.objects.get(id=gene_id)
            gene_code = gene.gene_code

            code = i['code']
            if code not in new_seqs:
                new_seqs[code] = {}
            del i['code']
            new_seqs[code][gene_code] = i['total_number_bp']
        return new_seqs

    def build_sequence_string(self, sequences):
        my_string = []
        for gene in self.genes:
            gene_code = gene['gene_code']
            try:
                my_string.append(str(sequences[gene_code]))
            except KeyError:
                my_string.append('')

        my_string = '<td>' + '</td><td>'.join(my_string) + '</td>'
        return my_string
