import json
import os
import re
from time import sleep

from django.conf import settings
from django.db import models
from django.db.models import SET_NULL
from django.db.models.signals import post_save

import flickrapi


class TimeStampedModel(models.Model):
    """Abstract base class for self-updating ``created`` and ``modified`` fields.

    Taken from the 'Two scoops of django' book (v1.8).
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return "Time created"


class Genes(models.Model):
    gene_code = models.CharField(max_length=100, unique=True)
    genetic_code = models.PositiveSmallIntegerField(
        null=True,
        help_text='Translation table (as number). '
                  'See <a href="http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi">http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi</a>',
    )
    length = models.PositiveSmallIntegerField(
        null=True,
        help_text='Number of base pairs',
    )
    description = models.CharField(max_length=255, blank=True,
                                   help_text='Long gene name.')
    reading_frame = models.PositiveSmallIntegerField(
        null=True,
        help_text='Either 1, 2 or 3',
    )
    notes = models.TextField(blank=True)
    aligned = models.CharField(
        max_length=6, choices=(
            ('yes', 'yes'),
            ('no', 'no'),
            ('notset', 'notset'),
        ),
        default='notset',
    )
    intron = models.CharField(max_length=255, blank=True)
    prot_code = models.CharField(
        max_length=6, choices=(
            ('yes', 'yes'),
            ('no', 'no'),
            ('notset', 'notset'),
        ),
        default='notset',
    )
    gene_type = models.CharField(max_length=255, blank=True, help_text='Nuclear, mitochondrial.')
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gene_code

    class Meta:
        verbose_name_plural = 'Genes'
        app_label = 'public_interface'


class GeneSets(models.Model):
    geneset_name = models.CharField(max_length=75, blank=False)
    geneset_creator = models.CharField(max_length=75, blank=False)
    geneset_description = models.CharField(max_length=140, blank=True)
    geneset_list = models.TextField(blank=False, help_text='As items separated by linebreak.')

    def save(self, *args, **kwargs):
        tmp = [i.strip() for i in self.geneset_list.splitlines() if len(i) > 0]
        self.geneset_list = '\n'.join(tmp)
        super(GeneSets, self).save(*args, **kwargs)

    def __str__(self):
        return self.geneset_name

    class Meta:
        verbose_name_plural = 'Gene sets'
        app_label = 'public_interface'


class TaxonSets(models.Model):
    taxonset_name = models.CharField(max_length=75, blank=False)
    taxonset_creator = models.CharField(max_length=75, blank=False)
    taxonset_description = models.CharField(max_length=140, blank=True)
    taxonset_list = models.TextField(help_text='As items separated by linebreak.')

    def save(self, *args, **kwargs):
        tmp = [i.strip() for i in self.taxonset_list.splitlines() if len(i) > 0]
        self.taxonset_list = '\n'.join(tmp)
        super(TaxonSets, self).save(*args, **kwargs)

    def __str__(self):
        return self.taxonset_name

    class Meta:
        verbose_name_plural = 'Taxon sets'
        app_label = 'public_interface'


class Vouchers(TimeStampedModel):
    MALE = 'male'
    FEMALE = 'female'
    LARVA = 'larva'
    WORKER = 'worker'
    QUEEN = 'queen'
    UNKNOWN = 'unknown'
    SEX_CHOICES = (
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
        (UNKNOWN, 'unknown'),
    )

    DONT_KNOW = 'unknown'
    YES = 'yes'
    NO = 'not'
    TYPE_SPECIES_CHOICES = (
        (DONT_KNOW, 'unknown'),
        (YES, 'yes'),
        (NO, 'not'),
    )

    SPREAD = 'spread'
    ENVELOPE = 'in envelope'
    PHOTO = 'only photo'
    NONE = 'no voucher'
    DESTROYED = 'destroyed'
    LOST = 'lost'
    VOUCHER_CHOICES = (
        (SPREAD, 'spread'),
        (ENVELOPE, 'in envelope'),
        (PHOTO, 'only photo'),
        (NONE, 'no voucher'),
        (DESTROYED, 'destroyed'),
        (LOST, 'lost'),
        (UNKNOWN, 'unknown'),
    )
    code = models.CharField(
        max_length=300, unique=True, primary_key=True, db_index=True, help_text="Voucher code.")
    orden = models.TextField(blank=True, db_index=True)
    superfamily = models.TextField(blank=True, db_index=True)
    family = models.TextField(blank=True, db_index=True)
    subfamily = models.TextField(blank=True, db_index=True)
    tribe = models.TextField(blank=True, db_index=True)
    subtribe = models.TextField(blank=True, db_index=True)
    genus = models.TextField(blank=True, db_index=True)
    species = models.TextField(blank=True, db_index=True)
    subspecies = models.TextField(blank=True, db_index=True)
    country = models.TextField(blank=True, db_index=True)
    specific_locality = models.TextField(
        help_text="Locality of origin for this specimen.", blank=True, db_index=True)
    type_species = models.CharField(
        max_length=100, choices=TYPE_SPECIES_CHOICES, help_text="Is this a type species?",
        db_index=True)
    latitude = models.FloatField(blank=True, null=True, db_index=True)
    longitude = models.FloatField(blank=True, null=True, db_index=True)
    max_altitude = models.IntegerField(
        blank=True, null=True, help_text="Enter altitude in meters above sea level.", db_index=True)
    min_altitude = models.IntegerField(
        blank=True, null=True, help_text="Enter altitude in meters above sea level.", db_index=True)
    collector = models.TextField(blank=True, db_index=True)
    date_collection = models.CharField(
        verbose_name="Date collection start", max_length=10, blank=True, db_index=True, default="",
        help_text="Enter date in format YYYY-mm-dd")
    date_collection_end = models.CharField(
        max_length=10, blank=True, help_text="Optional. Enter date in format YYYY-mm-dd",
        db_index=True)
    extraction = models.TextField(
        help_text="Number of extraction event.", blank=True, db_index=True)
    extraction_tube = models.TextField(
        help_text="Tube containing DNA extract.", blank=True, db_index=True)
    date_extraction = models.DateField(blank=True, null=True, db_index=True)
    extractor = models.TextField(blank=True, db_index=True)
    voucher_locality = models.TextField(blank=True, db_index=True)
    published_in = models.TextField(blank=True, null=True, db_index=True)
    notes = models.TextField(blank=True, null=True, db_index=True)
    edits = models.TextField(blank=True, null=True)
    latest_editor = models.TextField(blank=True, null=True, db_index=True)
    hostorg = models.TextField(help_text="Hostplant or other host.", blank=True, db_index=True)
    sex = models.CharField(max_length=100, choices=SEX_CHOICES, blank=True, db_index=True)
    voucher = models.CharField(
        max_length=100, choices=VOUCHER_CHOICES, blank=True, help_text="Voucher status.",
        db_index=True)
    voucher_code = models.TextField(
        help_text="Alternative code of voucher specimen.", blank=True, db_index=True)
    code_bold = models.TextField(
        help_text="Optional code for specimens kept in the BOLD database.", blank=True,
        db_index=True)
    determined_by = models.TextField(
        help_text="Person that identified the taxon for this specimen.", blank=True, db_index=True)
    author = models.TextField(
        help_text="Person that described this taxon.", blank=True, db_index=True)
    # temporal url used for batch upload
    flickr_photo_url = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Vouchers'
        app_label = 'public_interface'

    def __str__(self):
        return f"{self.code} {self.genus} {self.species}"

    def save(self, *args, **kwargs):
        super(Vouchers, self).save(*args, **kwargs)
        if self.flickr_photo_url and settings.PHOTOS_REPOSITORY == "flickr":
            photo_info = get_flickr_photo_info(self.flickr_photo_url)
            if photo_info:
                try:
                    FlickrImages.objects.get_or_create(
                        voucher=self,
                        thumbnail=photo_info['thumbnail_url'],
                        flickr_id=photo_info['photo_id'],
                        voucher_image=self.flickr_photo_url,
                    )
                except FlickrImages.MultipleObjectsReturned:
                    pass


def get_flickr_photo_info(flickr_photo_url):
    photo_info = {
        'thumbnail_url': '',
        'photo_id': '',
    }
    res = re.search(r'photos/\S+/([0-9]+)/?', flickr_photo_url)
    if res:
        photo_id = res.group(1)
        flickr = flickrapi.FlickrAPI(settings.FLICKR_API_KEY, settings.FLICKR_API_SECRET)
        try:
            info = flickr.photos.getInfo(photo_id=photo_id, format="json")
        except ConnectionError:
            try:
                sleep(2)
                info = flickr.photos.getInfo(photo_id=photo_id, format="json")
            except ConnectionError:
                info = None

        if not info:
            return None
        info = json.loads(info.decode('utf-8'))
        photo_info['thumbnail_url'] = make_flickr_thumbnail_url(info, photo_id)
        photo_info['photo_id'] = photo_id
        return photo_info

    return None


class Sequences(models.Model):
    code = models.ForeignKey(
        Vouchers, db_index=True, help_text='This is your voucher code.', on_delete=models.CASCADE
    )
    gene = models.ForeignKey(Genes, null=True, on_delete=SET_NULL)
    sequences = models.TextField(blank=True)
    accession = models.CharField(max_length=100, blank=True, db_index=True)
    lab_person = models.CharField(max_length=100, blank=True, db_index=True)
    time_created = models.DateTimeField(auto_now_add=True, null=True, blank=True, db_index=True)
    time_edited = models.DateTimeField(auto_now=True, null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True, db_index=True)
    genbank = models.BooleanField(db_index=True, default=False)
    total_number_bp = models.IntegerField(blank=True, null=True, db_index=True)
    number_ambiguous_bp = models.IntegerField(blank=True, null=True, db_index=True)

    class Meta:
        verbose_name_plural = 'Sequences'
        app_label = 'public_interface'

    def save(self, *args, **kwargs):
        if not self.gene:
            raise Exception(f'It is necessary to provide a value for column `gene`.')

        ambiguous_seq_length = self.sequences.count('?') + self.sequences.count('-')
        ambiguous_seq_length += self.sequences.count('N') + self.sequences.count('n')
        self.number_ambiguous_bp = ambiguous_seq_length
        self.total_number_bp = len(str(self.sequences))
        super(Sequences, self).save(*args, **kwargs)

    def __str__(self):
        return "sequence"


class Primers(models.Model):
    for_sequence = models.ForeignKey(
        Sequences,
        help_text='relation to Sequences table with reference for code and gene_code.',
        on_delete=models.SET_NULL,
        null=True,
    )
    primer_f = models.CharField(max_length=100, blank=True)
    primer_r = models.CharField(max_length=100, blank=True)

    class Meta:
        app_label = 'public_interface'

    def __str__(self):
        return "{0} -> <- {1}".format(self.primer_f, self.primer_r)


def make_flickr_thumbnail_url(info, photo_id):
    """
    Construct a url for the flicker photo using id and photo information as
    returned by their api method getInfo().
    """
    farm = info['photo']['farm']
    server = info['photo']['server']
    secret = info['photo']['secret']
    thumbnail_url = 'https://farm{0}.staticflickr.com/{1}/{2}_{3}_m_d.jpg'.format(
        farm, server, photo_id, secret
    )
    return thumbnail_url


class FlickrImages(models.Model):
    voucher = models.ForeignKey(
        Vouchers,
        help_text='Relation with id of voucher. Save as lower case.',
        db_index=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    voucher_image = models.URLField(
        help_text="Paste the URL of any Flicker image. Eg: https://www.flickr.com/photos/nsg_db/50905900296",
        blank=True,
    )
    thumbnail = models.URLField(help_text="URLs for the small sized image from Flickr.")
    flickr_id = models.CharField(max_length=100, help_text="ID numbers from Flickr for our photo.")
    image_file = models.ImageField(
        help_text="Upload a photo from your computer so we can send it to Flickr. ",
        blank=True
    )

    class Meta:
        verbose_name_plural = 'Flickr Images'
        app_label = 'public_interface'

    def save(self, *args, **kwargs):
        if self.voucher_image:
            # User pasted a photo url
            photo_info = get_flickr_photo_info(self.voucher_image)
            if not photo_info:
                return
            self.thumbnail = photo_info['thumbnail_url']
            self.flickr_id = photo_info['photo_id']
            super(FlickrImages, self).save(*args, **kwargs)
        else:
            post_save.connect(self.update_flickr_image, sender=FlickrImages, dispatch_uid="update_flickr_image_count")
            self.delete_local_photo(self.image_file)
            super(FlickrImages, self).save(*args, **kwargs)

    def delete_local_photo(self, image_filename):
        file_path = os.path.join(settings.MEDIA_ROOT, str(image_filename))
        if os.path.isfile(file_path):
            os.remove(file_path)

    def update_flickr_image(self, instance, **kwargs):
        my_api_key = settings.FLICKR_API_KEY
        my_secret = settings.FLICKR_API_SECRET
        flickr = flickrapi.FlickrAPI(my_api_key, my_secret)
        if not flickr.token_valid(perms="write"):
            raise Exception(
                "It is not possible to authenticate flickr automatically. "
                "It is necessary to do it manually. Contact your developer."
            )
            # flickr.get_request_token(oauth_callback='oob')

        filename = os.path.join(settings.MEDIA_ROOT, str(instance.image_file))

        if instance.flickr_id == '':
            title = self.make_title(instance)
            description = self.make_description(instance)
            tags = self.make_tags(instance)

            rsp = flickr.upload(filename, title=title, description=description,
                                tags=tags)

            instance.flickr_id = rsp.findtext('photoid')

            info = flickr.photos.getInfo(photo_id=instance.flickr_id, format="json")
            info = json.loads(info.decode('utf-8'))
            instance.voucher_image = info['photo']['urls']['url'][0]['_content']

            thumbnail_url = make_flickr_thumbnail_url(info, instance.flickr_id)
            instance.thumbnail = thumbnail_url
            instance.save()

    def make_title(self, instance):
        title = '{0} {1} {2}'.format(
            instance.voucher.code,
            instance.voucher.genus,
            instance.voucher.species,
        )
        return title

    def make_description(self, instance):
        description = '{0}. {1}. {2}'.format(
            instance.voucher.country,
            instance.voucher.specific_locality,
            instance.voucher.published_in,
        )
        return description

    def make_tags(self, instance):
        tags = [
            instance.voucher.country,
            instance.voucher.family,
            instance.voucher.subfamily,
            instance.voucher.tribe,
            instance.voucher.subtribe,
            instance.voucher.genus,
            instance.voucher.species,
        ]
        tags = '"' + '" "'.join(tags) + '"'
        return tags

    def __str__(self):
        return "{0} {1}".format(self.voucher, self.voucher_image)


class LocalImages(models.Model):
    """Voucher images saved in local system."""
    voucher = models.ForeignKey(
        Vouchers,
        help_text='Relation with id of voucher.',
        db_index=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    voucher_image = models.ImageField(help_text="voucher photo.", blank=True)

    class Meta:
        verbose_name_plural = 'Local Images'
        app_label = 'public_interface'

    def __str__(self):
        return "{0} {1}".format(self.voucher, self.voucher_image)
