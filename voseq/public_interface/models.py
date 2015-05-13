import json

from django.db import models


class Genes(models.Model):
    gene_code = models.CharField(max_length=100)
    genetic_code = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text='Translation table',
    )
    length = models.PositiveSmallIntegerField(blank=True, null=True)
    description = models.CharField(max_length=255, blank=True)
    reading_frame = models.PositiveSmallIntegerField(blank=True, null=True)
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
    gene_type = models.CharField(max_length=255, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.gene_code


class GeneSets(models.Model):
    geneset_name = models.CharField(max_length=75, blank=False)
    geneset_creator = models.CharField(max_length=75, blank=False)
    geneset_description = models.CharField(max_length=140, blank=True)
    geneset_list = models.TextField(blank=False)

    def save(self, *args, **kwargs):
        self.geneset_list = json.dumps(self.geneset_list)
        super(GeneSets, self).save(*args, **kwargs)

    def __str__(self):
        return self.geneset_name


class Members(models.Model):
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    login = models.CharField(max_length=100)
    passwd = models.CharField(max_length=100)
    admin = models.BinaryField(default=None)


class TaxonSets(models.Model):
    taxonset_name = models.CharField(max_length=75, blank=False)
    taxonset_creator = models.CharField(max_length=75, blank=False)
    taxonset_description = models.CharField(max_length=140, blank=True)
    taxonset_list = models.TextField()

    def save(self, *args, **kwargs):
        self.taxonset_list = json.dumps(self.taxonset_list)
        super(TaxonSets, self).save(*args, **kwargs)

    def __str__(self):
        return self.taxonset_name


class Vouchers(models.Model):
    MALE = 'm'
    FEMALE = 'f'
    LARVA = 'l'
    WORKER = 'w'
    QUEEN = 'q'
    UNKNOWN = 'u'
    SEX_CHOICES = (
        (MALE, 'male'),
        (FEMALE, 'female'),
        (LARVA, 'larva'),
        (WORKER, 'worker'),
        (QUEEN, 'queen'),
        (UNKNOWN, 'unknown'),
    )

    DONT_KNOW = 'd'
    YES = 'y'
    NO = 'n'
    TYPE_SPECIES_CHOICES = (
        (DONT_KNOW, 'don\'t know'),
        (YES, 'yes'),
        (NO, 'no'),
    )

    SPREAD = 's'
    ENVELOPE = 'e'
    PHOTO = 'p'
    NONE = 'n'
    DESTROYED = 'd'
    LOST = 'l'
    VOUCHER_CHOICES = (
        (SPREAD, 'spread'),
        (ENVELOPE, 'in envelope'),
        (PHOTO, 'only photo'),
        (NONE, 'no voucher'),
        (DESTROYED, 'destroyed'),
        (LOST, 'lost'),
        (UNKNOWN, 'unknown'),
    )
    code = models.CharField(max_length=100, unique=True,
                            primary_key=True,
                            help_text="Voucher code.",
                            )
    orden = models.CharField(max_length=100, blank=True)
    superfamily = models.CharField(max_length=100, blank=True)
    family = models.CharField(max_length=100, blank=True)
    subfamily = models.CharField(max_length=100, blank=True)
    tribe = models.CharField(max_length=100, blank=True)
    subtribe = models.CharField(max_length=100, blank=True)
    genus = models.CharField(max_length=100, blank=True)
    species = models.CharField(max_length=100, blank=True)
    subspecies = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    specificLocality = models.CharField(max_length=250, help_text="Locality of origin for this specimen.", blank=True)
    typeSpecies = models.CharField(max_length=1, choices=TYPE_SPECIES_CHOICES,
                                   help_text="Is this a type species?")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    max_altitude = models.IntegerField(blank=True, null=True, help_text="Enter altitude in meters above sea level.")
    min_altitude = models.IntegerField(blank=True, null=True, help_text="Enter altitude in meters above sea level.")
    collector = models.CharField(max_length=100, blank=True)
    dateCollection = models.DateField(null=True)  # TODO check if better blank null rather than null true
    extraction = models.CharField(max_length=50, help_text="Number of extraction event.", blank=True)
    extractionTube = models.CharField(max_length=50, help_text="Tube containing DNA extract.", blank=True)
    dateExtraction = models.DateField(null=True)
    extractor = models.CharField(max_length=100, blank=True)
    voucherLocality = models.CharField(max_length=200, blank=True)
    publishedIn = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    edits = models.TextField(blank=True, null=True)
    latesteditor = models.TextField(blank=True, null=True)
    hostorg = models.CharField(max_length=200, help_text="Hostplant or other host.", blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)
    voucher = models.CharField(max_length=1, choices=VOUCHER_CHOICES, blank=True,
                               help_text="Voucher status.")
    voucherCode = models.CharField(max_length=100, help_text="Alternative code of voucher specimen.", blank=True)
    code_bold = models.CharField(max_length=100, help_text="Optional code for specimens kept in the BOLD database.", blank=True)
    determinedBy = models.CharField(max_length=100, help_text="Person that identified the taxon for this specimen.", blank=True)
    author = models.CharField(max_length=100, help_text="Person that described this taxon.", blank=True)
    timestamp = models.DateTimeField(null=True)  # TODO change this to date_created = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Vouchers"


class Sequences(models.Model):
    code = models.ForeignKey(Vouchers, help_text='Save as lower case.')
    gene_code = models.CharField(max_length=100)
    sequences = models.TextField(blank=True)
    accession = models.CharField(max_length=100, blank=True)
    labPerson = models.CharField(max_length=100, blank=True)
    time_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    time_edited = models.DateTimeField(auto_now=True, null=True, blank=True)
    notes = models.TextField(blank=True)
    genbank = models.BooleanField()
    number_ambiguous_bp = models.IntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        ambiguous_seq_length = self.sequences.count('?') + self.sequences.count('-')
        ambiguous_seq_length += self.sequences.count('N') + self.sequences.count('n')
        self.number_ambiguous_bp = ambiguous_seq_length
        super(Sequences, self).save(*args, **kwargs)


class Primers(models.Model):
    for_sequence = models.ForeignKey(Sequences, help_text='relation to Sequences table with reference '
                                                          'for code and gene_code.')
    primer_f = models.CharField(max_length=100, blank=True)
    primer_r = models.CharField(max_length=100, blank=True)


class FlickrImages(models.Model):
    voucher = models.ForeignKey(
        Vouchers,
        help_text='Relation with id of voucher. Save as lower case.',
    )
    voucherImage = models.URLField(help_text="URLs of the Flickr page.")
    thumbnail = models.URLField(help_text="URLs for the small sized image from Flickr.")
    flickr_id = models.CharField(max_length=100, help_text="ID numbers from Flickr for our photo.")
