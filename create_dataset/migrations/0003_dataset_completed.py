# Generated by Django 2.2.13 on 2020-11-01 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create_dataset', '0002_dataset_task_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='completed',
            field=models.DateTimeField(null=True),
        ),
    ]
