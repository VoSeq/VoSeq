from django.db import models


class OverviewTable(models.Model):
    """Bulk create does not work on inherited models so we need to create a new
    one.
    """
    sequence_string = models.TextField(help_text="HTML string of cells with length of"
                                                 "sequences for each gene.")
    o_code = models.CharField(max_length=300)
    orden = models.TextField(blank=True)
    superfamily = models.TextField(blank=True)
    family = models.TextField(blank=True)
    subfamily = models.TextField(blank=True)
    genus = models.TextField(blank=True)
    species = models.TextField(blank=True)
