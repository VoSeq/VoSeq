from django.contrib.auth.models import User
from django.db import models


class Dataset(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.DateTimeField(null=True)
    content = models.TextField(null=True)
    task_id = models.TextField(null=True)
    # TODO: add warnings
