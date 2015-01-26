from django.shortcuts import render

from core.utils import get_version_stats
from public_interface.models import Genes


def index(request):
    version, stats = get_version_stats()

    queryset = Genes.objects.all()
    return render(request, 'view_genes/index.html',
                  {
                      'result': queryset,
                      'version': version,
                      'stats': stats,
                  },
                  )


def gene(request, gene_code):
    version, stats = get_version_stats()

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
                      'item': item,
                      'version': version,
                      'stats': stats,
                  },
                  )
