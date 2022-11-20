from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField


class Dataset(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True)
    content = models.TextField(null=True)
    task_id = models.TextField(null=True)
    errors = JSONField(blank=True, null=True)
    warnings = JSONField(blank=True, null=True)
    # genbank datasets require nucleotidae and aminoacid datasets
    sister_dataset_id = models.IntegerField(null=True, blank=True)
    # eg. Phylip datasets require an extra part for the gene definitions
    charset_block = models.TextField(null=True)
    task_uuid = models.TextField(null=True, blank=True)
    progress = models.CharField(max_length=200, blank=True, null=True)
