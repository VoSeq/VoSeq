import logging
import os

from celery import chord, chain, uuid
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from create_dataset.tasks import create_dataset
from core.utils import get_context
from create_dataset.models import Dataset
from public_interface.tasks import log_email_error, notify_user
from .forms import GenBankFastaForm


log = logging.getLogger(__name__)


@login_required
def index(request):
    form = GenBankFastaForm()
    context = get_context(request)
    context["form"] = form
    return render(request, 'genbank_fasta/index.html', context)


@login_required
def generate_results(request):
    context = get_context(request)

    if request.method == 'POST':
        form = GenBankFastaForm(request.POST)

        if form.is_valid():
            dataset_obj_id = schedule_genbank_fasta(form.cleaned_data, request.user)
            return HttpResponseRedirect(
                reverse(
                    'create-genbank-results',
                    kwargs={'dataset_id': dataset_obj_id}
                )
            )
        else:
            log.debug("invalid form")
            context["form"] = form
            return render(request, 'genbank_fasta/index.html', context)


def schedule_genbank_fasta(cleaned_data, user) -> int:
    if cleaned_data['taxonset']:
        taxonset_id = cleaned_data['taxonset'].id
    else:
        taxonset_id = None

    if cleaned_data['geneset']:
        geneset_id = cleaned_data['geneset'].id
    else:
        geneset_id = None

    gene_codes_ids = list(cleaned_data['gene_codes'].values_list('id', flat=True))
    voucher_codes = cleaned_data['voucher_codes']
    file_format = 'GenBankFASTA'
    outgroup = ''
    positions = 'ALL'
    partition_by_positions = 'by gene'
    translations = False
    aminoacids = False
    degen_translations = ''
    special = ''
    taxon_names = ['CODE', 'GENUS', 'SPECIES']
    number_genes = ''
    introns = ''

    task_id = uuid()
    nucleotide_dataset_obj = Dataset.objects.create(
        user=user, task_uuid=task_id
    )
    aa_dataset_obj = Dataset.objects.create(
        user=user,
        sister_dataset_id=nucleotide_dataset_obj.id,
        task_uuid=task_id,
    )
    dataset_tasks = chain(
        create_dataset.si(
            taxonset_id,
            geneset_id,
            gene_codes_ids,
            voucher_codes,
            file_format,
            outgroup,
            positions,
            partition_by_positions,
            translations,
            aminoacids,
            degen_translations,
            special,
            taxon_names,
            number_genes,
            introns,
            nucleotide_dataset_obj.id,
        ).on_error(log_email_error.s(user.id)),
        create_dataset.si(
            taxonset_id,
            geneset_id,
            gene_codes_ids,
            voucher_codes,
            file_format,
            outgroup,
            positions,
            partition_by_positions,
            translations,
            True,
            degen_translations,
            special,
            taxon_names,
            number_genes,
            introns,
            aa_dataset_obj.id,
        ).on_error(log_email_error.s(user.id)),
    )
    tasks = chord(
        header=dataset_tasks,
        body=notify_user.si(aa_dataset_obj.id, user.id)
    )
    tasks.apply_async(task_id=task_id)
    return aa_dataset_obj.id


@login_required
@csrf_exempt
def results(request, dataset_id):
    context = get_context(request)

    try:
        aa_dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        raise Http404(f'such dataset {dataset_id} does not exist')

    try:
        nucleotide_dataset = Dataset.objects.get(
            id=aa_dataset.sister_dataset_id
        )
    except Dataset.DoesNotExist:
        raise Http404(f'such dataset {dataset_id} does not exist')

    context['task_status'] = ''
    if nucleotide_dataset.task_uuid:
        task_results = AsyncResult(nucleotide_dataset.task_uuid)
        context['task_status'] = task_results.state
    context['errors'] = list(nucleotide_dataset.errors or []) + list(aa_dataset.errors or [])
    context['warnings'] = list(nucleotide_dataset.warnings or []) + list(aa_dataset.warnings or [])
    context['nucleotide_dataset'] = nucleotide_dataset
    context['aa_dataset'] = aa_dataset
    return render(request, 'genbank_fasta/results.html', context)


@login_required
def serve_file(request, file_name):
    log.debug("Requested file by user: {0}".format(request.user))
    cwd = os.path.dirname(__file__)
    fasta_file = os.path.join(cwd,
                              '..',
                              'create_dataset',
                              'dataset_files',
                              file_name,
                              )
    response = HttpResponse(open(fasta_file, 'r').read(), content_type='application/text')
    response['Content-Disposition'] = 'attachment; filename=voseq_genbank.fasta'

    if os.path.isfile(fasta_file):
        os.remove(fasta_file)
    return response
