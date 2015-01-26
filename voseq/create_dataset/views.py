from django.shortcuts import render

from .forms import CreateDatasetForm


def index(request):
    form = CreateDatasetForm()

    return render(request,
                  'create_dataset/index.html',
                  {
                      'form': form,
                  },
                  )
