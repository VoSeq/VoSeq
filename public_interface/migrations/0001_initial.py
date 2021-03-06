# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2020-03-22 00:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlickrImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_image', models.URLField(blank=True, help_text='URLs of the Flickr page.')),
                ('thumbnail', models.URLField(help_text='URLs for the small sized image from Flickr.')),
                ('flickr_id', models.CharField(help_text='ID numbers from Flickr for our photo.', max_length=100)),
                ('image_file', models.ImageField(blank=True, help_text='Placeholder for image file so we can send it to Flickr. The file has been deleted right after upload.', upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Flickr Images',
            },
        ),
        migrations.CreateModel(
            name='Genes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_code', models.CharField(max_length=100)),
                ('genetic_code', models.PositiveSmallIntegerField(help_text='Translation table (as number). See <a href="http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi">http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi</a>', null=True)),
                ('length', models.PositiveSmallIntegerField(help_text='Number of base pairs', null=True)),
                ('description', models.CharField(blank=True, help_text='Long gene name.', max_length=255)),
                ('reading_frame', models.PositiveSmallIntegerField(help_text='Either 1, 2 or 3', null=True)),
                ('notes', models.TextField(blank=True)),
                ('aligned', models.CharField(choices=[('yes', 'yes'), ('no', 'no'), ('notset', 'notset')], default='notset', max_length=6)),
                ('intron', models.CharField(blank=True, max_length=255)),
                ('prot_code', models.CharField(choices=[('yes', 'yes'), ('no', 'no'), ('notset', 'notset')], default='notset', max_length=6)),
                ('gene_type', models.CharField(blank=True, help_text='Nuclear, mitochondrial.', max_length=255)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'Genes',
            },
        ),
        migrations.CreateModel(
            name='GeneSets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geneset_name', models.CharField(max_length=75)),
                ('geneset_creator', models.CharField(max_length=75)),
                ('geneset_description', models.CharField(blank=True, max_length=140)),
                ('geneset_list', models.TextField(help_text='As items separated by linebreak.')),
            ],
            options={
                'verbose_name_plural': 'Gene sets',
            },
        ),
        migrations.CreateModel(
            name='LocalImages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voucher_image', models.ImageField(blank=True, help_text='voucher photo.', upload_to='')),
            ],
            options={
                'verbose_name_plural': 'Local Images',
            },
        ),
        migrations.CreateModel(
            name='Primers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primer_f', models.CharField(blank=True, max_length=100)),
                ('primer_r', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Sequences',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_code', models.CharField(db_index=True, max_length=100)),
                ('sequences', models.TextField(blank=True)),
                ('accession', models.CharField(blank=True, db_index=True, max_length=100)),
                ('lab_person', models.CharField(blank=True, db_index=True, max_length=100)),
                ('time_created', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('time_edited', models.DateTimeField(auto_now=True, db_index=True, null=True)),
                ('notes', models.TextField(blank=True, db_index=True)),
                ('genbank', models.NullBooleanField(db_index=True)),
                ('total_number_bp', models.IntegerField(blank=True, db_index=True, null=True)),
                ('number_ambiguous_bp', models.IntegerField(blank=True, db_index=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Sequences',
            },
        ),
        migrations.CreateModel(
            name='TaxonSets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('taxonset_name', models.CharField(max_length=75)),
                ('taxonset_creator', models.CharField(max_length=75)),
                ('taxonset_description', models.CharField(blank=True, max_length=140)),
                ('taxonset_list', models.TextField(help_text='As items separated by linebreak.')),
            ],
            options={
                'verbose_name_plural': 'Taxon sets',
            },
        ),
        migrations.CreateModel(
            name='Vouchers',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('code', models.CharField(db_index=True, help_text='Voucher code.', max_length=300, primary_key=True, serialize=False, unique=True)),
                ('orden', models.TextField(blank=True, db_index=True)),
                ('superfamily', models.TextField(blank=True, db_index=True)),
                ('family', models.TextField(blank=True, db_index=True)),
                ('subfamily', models.TextField(blank=True, db_index=True)),
                ('tribe', models.TextField(blank=True, db_index=True)),
                ('subtribe', models.TextField(blank=True, db_index=True)),
                ('genus', models.TextField(blank=True, db_index=True)),
                ('species', models.TextField(blank=True, db_index=True)),
                ('subspecies', models.TextField(blank=True, db_index=True)),
                ('country', models.TextField(blank=True, db_index=True)),
                ('specific_locality', models.TextField(blank=True, db_index=True, help_text='Locality of origin for this specimen.')),
                ('type_species', models.CharField(choices=[('unknown', 'unknown'), ('yes', 'yes'), ('not', 'not')], db_index=True, help_text='Is this a type species?', max_length=100)),
                ('latitude', models.FloatField(blank=True, db_index=True, null=True)),
                ('longitude', models.FloatField(blank=True, db_index=True, null=True)),
                ('max_altitude', models.IntegerField(blank=True, db_index=True, help_text='Enter altitude in meters above sea level.', null=True)),
                ('min_altitude', models.IntegerField(blank=True, db_index=True, help_text='Enter altitude in meters above sea level.', null=True)),
                ('collector', models.TextField(blank=True, db_index=True)),
                ('date_collection', models.CharField(blank=True, db_index=True, default='', help_text='Enter date in format YYYY-mm-dd', max_length=10, verbose_name='Date collection start')),
                ('date_collection_end', models.CharField(blank=True, db_index=True, help_text='Optional. Enter date in format YYYY-mm-dd', max_length=10)),
                ('extraction', models.TextField(blank=True, db_index=True, help_text='Number of extraction event.')),
                ('extraction_tube', models.TextField(blank=True, db_index=True, help_text='Tube containing DNA extract.')),
                ('date_extraction', models.DateField(blank=True, db_index=True, null=True)),
                ('extractor', models.TextField(blank=True, db_index=True)),
                ('voucher_locality', models.TextField(blank=True, db_index=True)),
                ('published_in', models.TextField(blank=True, db_index=True, null=True)),
                ('notes', models.TextField(blank=True, db_index=True, null=True)),
                ('edits', models.TextField(blank=True, null=True)),
                ('latest_editor', models.TextField(blank=True, db_index=True, null=True)),
                ('hostorg', models.TextField(blank=True, db_index=True, help_text='Hostplant or other host.')),
                ('sex', models.CharField(blank=True, choices=[('male', 'male'), ('female', 'female'), ('larva', 'larva'), ('worker', 'worker'), ('queen', 'queen'), ('unknown', 'unknown')], db_index=True, max_length=100)),
                ('voucher', models.CharField(blank=True, choices=[('spread', 'spread'), ('in envelope', 'in envelope'), ('only photo', 'only photo'), ('no voucher', 'no voucher'), ('destroyed', 'destroyed'), ('lost', 'lost'), ('unknown', 'unknown')], db_index=True, help_text='Voucher status.', max_length=100)),
                ('voucher_code', models.TextField(blank=True, db_index=True, help_text='Alternative code of voucher specimen.')),
                ('code_bold', models.TextField(blank=True, db_index=True, help_text='Optional code for specimens kept in the BOLD database.')),
                ('determined_by', models.TextField(blank=True, db_index=True, help_text='Person that identified the taxon for this specimen.')),
                ('author', models.TextField(blank=True, db_index=True, help_text='Person that described this taxon.')),
            ],
            options={
                'verbose_name_plural': 'Vouchers',
            },
        ),
        migrations.AddField(
            model_name='sequences',
            name='code',
            field=models.ForeignKey(help_text='This is your voucher code.', on_delete=django.db.models.deletion.CASCADE, to='public_interface.Vouchers'),
        ),
        migrations.AddField(
            model_name='primers',
            name='for_sequence',
            field=models.ForeignKey(help_text='relation to Sequences table with reference for code and gene_code.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='public_interface.Sequences'),
        ),
        migrations.AddField(
            model_name='localimages',
            name='voucher',
            field=models.ForeignKey(help_text='Relation with id of voucher.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='public_interface.Vouchers'),
        ),
        migrations.AddField(
            model_name='flickrimages',
            name='voucher',
            field=models.ForeignKey(help_text='Relation with id of voucher. Save as lower case.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='public_interface.Vouchers'),
        ),
    ]
