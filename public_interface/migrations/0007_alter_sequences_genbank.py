# Generated by Django 4.1.3 on 2022-11-20 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('public_interface', '0006_vouchers_flickr_photo_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequences',
            name='genbank',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
