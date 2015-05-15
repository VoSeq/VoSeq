from django.shortcuts import render

from .forms import GeneTableForm


def index(request):
    form = GeneTableForm()

    return render(request, 'gene_table/index.html',
                  {
                      'form': form,
                  },
                  )
