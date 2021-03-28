import logging

from celery import chord, group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.http import HttpResponse
from django.urls import reverse

from core.utils import get_context
from public_interface.tasks import log_email_error, notify_user
from .forms import CreateDatasetForm
from create_dataset.models import Dataset
from .tasks import create_dataset


log = logging.getLogger(__name__)


@login_required
def index(request):
    form = CreateDatasetForm()
    context = get_context(request)
    context["form"] = form

    return render(request, 'create_dataset/index.html', context)


@login_required
def generate_results(request):
    context = get_context(request)

    if request.method == 'POST':
        form = CreateDatasetForm(request.POST)

        if form.is_valid():
            dataset_obj_id = schedule_dataset(form.cleaned_data, request.user)
            return HttpResponseRedirect(reverse('create-dataset-results', kwargs={'dataset_id': dataset_obj_id}))
        else:
            log.debug("invalid form")
            context["form"] = form
            return render(request, 'create_dataset/index.html', context)


@login_required
def results(request, dataset_id):
    context = get_context(request)
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        raise Http404(f'such dataset {dataset_id} does not exist')

    context['dataset'] = dataset
    return render(request, 'create_dataset/results.html', context)


@login_required
def serve_file(request, dataset_id):
    # final_name = guess_file_extension(file_name)
    final_name = f'dataset_{dataset_id}.txt'
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        raise Http404(f'such dataset {dataset_id} does not exist')

    if dataset.completed:
        response = HttpResponse(dataset.content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename={}'.format(final_name)
        return response
    else:
        context = {'dataset_job_id': dataset_id}
        return render(request, 'create_dataset/results.html', context)


def schedule_dataset(cleaned_data, user) -> int:
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
    file_format = cleaned_data['file_format']
    outgroup = cleaned_data['outgroup']
    positions = cleaned_data['positions']
    partition_by_positions = cleaned_data['partition_by_positions']
    translations = cleaned_data['translations']
    aminoacids = cleaned_data['aminoacids']
    degen_translations = cleaned_data['degen_translations']
    special = cleaned_data['special']
    taxon_names = cleaned_data['taxon_names']
    number_genes = cleaned_data['number_genes']
    introns = cleaned_data['introns']

    nucleotide_dataset_obj = Dataset.objects.create(
        user=user
    )
    if file_format == "bankit":
        aa_dataset_obj = Dataset.objects.create(
            user=user,
            sister_dataset_id=nucleotide_dataset_obj.id,
        )

    dataset_tasks = [
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
    ]
    if file_format == "bankit":
        dataset_tasks.append(
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
            header=group(dataset_tasks),
            body=notify_user.si(aa_dataset_obj.id, user.id)
        )
        tasks.apply_async()
        return aa_dataset_obj.id
    else:
        tasks = chord(
            header=group(dataset_tasks),
            body=notify_user.si(nucleotide_dataset_obj.id, user.id)
        )
        tasks.apply_async()
        return nucleotide_dataset_obj.id

