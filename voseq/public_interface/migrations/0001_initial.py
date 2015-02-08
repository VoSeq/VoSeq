# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlickrImages',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('voucherImage', models.URLField(help_text='URLs of the Flickr page.')),
                ('thumbnail', models.URLField(help_text='URLs for the small sized image from Flickr.')),
                ('flickr_id', models.CharField(max_length=100, help_text='ID numbers from Flickr for our photo.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Genes',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('gene_code', models.CharField(max_length=100)),
                ('genetic_code', models.PositiveSmallIntegerField(blank=True, help_text='Translation table', null=True)),
                ('length', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('reading_frame', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('aligned', models.CharField(default='notset', max_length=6, choices=[('yes', 'yes'), ('no', 'no'), ('notset', 'notset')])),
                ('intron', models.CharField(blank=True, max_length=255)),
                ('prot_code', models.CharField(default='notset', max_length=6, choices=[('yes', 'yes'), ('no', 'no'), ('notset', 'notset')])),
                ('gene_type', models.CharField(blank=True, max_length=255)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeneSets',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('geneset_name', models.CharField(max_length=75)),
                ('geneset_creator', models.CharField(max_length=75)),
                ('geneset_description', models.CharField(blank=True, max_length=140)),
                ('geneset_list', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Members',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=100)),
                ('lastname', models.CharField(max_length=100)),
                ('login', models.CharField(max_length=100)),
                ('passwd', models.CharField(max_length=100)),
                ('admin', models.BinaryField(default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Primers',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('primer_f', models.CharField(blank=True, max_length=100)),
                ('primer_r', models.CharField(blank=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Sequences',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('gene_code', models.CharField(max_length=100)),
                ('sequences', models.TextField(blank=True)),
                ('accession', models.CharField(blank=True, max_length=100)),
                ('labPerson', models.CharField(blank=True, max_length=100)),
                ('time_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('time_edited', models.DateTimeField(auto_now=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('genbank', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TaxonSets',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('taxonset_name', models.CharField(max_length=75)),
                ('taxonset_creator', models.CharField(max_length=75)),
                ('taxonset_description', models.CharField(blank=True, max_length=140)),
                ('taxonset_list', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vouchers',
            fields=[
                ('code', models.CharField(serialize=False, unique=True, max_length=100, primary_key=True, help_text='Voucher code.')),
                ('orden', models.CharField(blank=True, max_length=100)),
                ('superfamily', models.CharField(blank=True, max_length=100)),
                ('family', models.CharField(blank=True, max_length=100)),
                ('subfamily', models.CharField(blank=True, max_length=100)),
                ('tribe', models.CharField(blank=True, max_length=100)),
                ('subtribe', models.CharField(blank=True, max_length=100)),
                ('genus', models.CharField(blank=True, max_length=100)),
                ('species', models.CharField(blank=True, max_length=100)),
                ('subspecies', models.CharField(blank=True, max_length=100)),
                ('country', models.CharField(blank=True, max_length=100)),
                ('specificLocality', models.CharField(blank=True, max_length=250, help_text='Locality of origin for this specimen.')),
                ('typeSpecies', models.CharField(blank=True, choices=[('d', "don't know"), ('y', 'yes'), ('n', 'no')], max_length=1, help_text='Is this a type species?')),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('max_altitude', models.IntegerField(blank=True, help_text='Enter altitude in meters above sea level.', null=True)),
                ('min_altitude', models.IntegerField(blank=True, help_text='Enter altitude in meters above sea level.', null=True)),
                ('collector', models.CharField(blank=True, max_length=100)),
                ('dateCollection', models.DateField(null=True)),
                ('extraction', models.CharField(blank=True, max_length=50, help_text='Number of extraction event.')),
                ('extractionTube', models.CharField(blank=True, max_length=50, help_text='Tube containing DNA extract.')),
                ('dateExtraction', models.DateField(null=True)),
                ('extractor', models.CharField(blank=True, max_length=100)),
                ('voucherLocality', models.CharField(blank=True, max_length=200)),
                ('publishedIn', models.TextField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('edits', models.TextField(blank=True, null=True)),
                ('latesteditor', models.TextField(blank=True, null=True)),
                ('hostorg', models.CharField(blank=True, max_length=200, help_text='Hostplant or other host.')),
                ('sex', models.CharField(blank=True, choices=[('m', 'male'), ('f', 'female'), ('l', 'larva'), ('w', 'worker'), ('q', 'queen')], max_length=1)),
                ('voucher', models.CharField(blank=True, choices=[('s', 'spread'), ('e', 'in envelope'), ('p', 'only photo'), ('n', 'no voucher'), ('d', 'destroyed'), ('l', 'lost')], max_length=1)),
                ('voucherCode', models.CharField(blank=True, max_length=100, help_text='Original code of voucher specimen.')),
                ('code_bold', models.CharField(blank=True, max_length=100, help_text='Optional code for specimens kept in the BOLD database.')),
                ('determinedBy', models.CharField(blank=True, max_length=100, help_text='Person that identified the taxon for this specimen.')),
                ('author', models.CharField(blank=True, max_length=100, help_text='Person that described this taxon.')),
                ('timestamp', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='sequences',
            name='code',
            field=models.ForeignKey(to='public_interface.Vouchers', help_text='Save as lower case.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='primers',
            name='for_sequence',
            field=models.ForeignKey(to='public_interface.Sequences', help_text='relation to Sequences table with reference for code and gene_code.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flickrimages',
            name='voucher',
            field=models.ForeignKey(to='public_interface.Vouchers', help_text='Relation with id of voucher. Save as lower case.'),
            preserve_default=True,
        ),
    ]
