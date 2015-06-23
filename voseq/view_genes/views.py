from django.shortcuts import render

from core.utils import get_version_stats
from core.utils import get_username
from public_interface.models import Genes
from stats.models import VouchersPerGene


def index(request):
    version, stats = get_version_stats()
    username = get_username(request)

    voucher_count = get_voucher_count()

    queryset = Genes.objects.all().values()
    result = []
    for i in queryset:
        gene_code = i['gene_code']
        i['voucher_count'] = voucher_count[gene_code]
        result.append(i)

    return render(request, 'view_genes/index.html',
                  {
                      'username': username,
                      'result': result,
                      'version': version,
                      'stats': stats,
                  },
                  )


def get_voucher_count():
    voucher_count = {}
    queryset = VouchersPerGene.objects.all().values('gene_code', 'voucher_count')
    for i in queryset:
        gene_code = i['gene_code']
        voucher_count[gene_code] = i['voucher_count']
    return voucher_count


def gene(request, gene_code):
    version, stats = get_version_stats()
    username = get_username(request)

    queryset = Genes.objects.filter(gene_code=gene_code)
    if len(queryset) < 1:
        item = ''
    else:
        item = queryset[0]

        if ';' in item.intron:
            introns = item.intron.split(';')
            j = 1
            out = ''
            for i in introns:
                out += '<b>Intron ' + str(j) + ':</b> ' + i + ' > '
                j += 1
            item.intron = out.rstrip(' > ')

    return render(request, 'view_genes/gene.html',
                  {
                      'username': username,
                      'item': item,
                      'version': version,
                      'stats': stats,
                  },
                  )
