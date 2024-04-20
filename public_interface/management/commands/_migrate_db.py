# -*- coding: future_fstrings -*-
"""
Needs an XML file with the database dump from MySQL:

> mysqldump --xml database > dump.xml
"""
from collections import namedtuple
import datetime
from os.path import basename
import pytz
import re
from urllib import parse
import sys
import xml.etree.ElementTree as ET

from Bio.Alphabet import IUPAC
import pyprind
from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError

from public_interface.models import Vouchers
from public_interface.models import FlickrImages
from public_interface.models import LocalImages
from public_interface.models import Sequences
from public_interface.models import Primers
from public_interface.models import Genes
from public_interface.models import GeneSets
from public_interface.models import TaxonSets


TZINFO = pytz.utc

TESTING = bool(settings.TESTING)


class ParseXML(object):
    """
    Parses MySQL dump as XML file.
    """
    def __init__(self, xml_string, tables_prefix = None, verbosity = 2):
        if tables_prefix is None:
            self.tables_prefix = ''
        else:
            self.tables_prefix = tables_prefix

        self.dump_string = xml_string
        self.table_genes_items = None
        self.table_genesets_items = None
        self.table_members_items = None
        self.table_primers_items = None
        self.table_sequences_items = None
        self.table_taxonsets_items = None
        self.table_vouchers_items = None
        self.table_flickr_images_items = []
        self.table_local_images_items = []
        self.list_of_voucher_codes = []
        self.verbosity = int(verbosity)

    def parse_image_info(self, item):
        """
        Returns tuple (is in Flickr, image data,)

        :param item:
        :return:
        """
        got_flickr = self.test_if_photo_in_flickr(item)
        if item['voucher_image'] == 'na.gif' or item['thumbnail'] == 'na.gif':
            return None, None

        item['voucher_image'] = get_as_tuple(item['voucher_image'], got_flickr)
        item['thumbnail'] = get_as_tuple(item['thumbnail'], got_flickr)

        imgs = []
        if got_flickr and item['flickr_id']:
            item['flickr_id'] = get_as_tuple(item['flickr_id'], got_flickr)

            for idx, i in enumerate(item['voucher_image']):
                try:
                    thumbnail = item['thumbnail'][idx]
                except IndexError:
                    thumbnail = ""
                imgs.append({
                    'voucher_id': item['code'],
                    'voucher_image': item['voucher_image'][idx],
                    'thumbnail': thumbnail,
                    'flickr_id': item['flickr_id'][idx],
                })
            return True, imgs
        else:
            for i in range(0, len(item['voucher_image']), 1):
                imgs.append({
                    'voucher_id': item['code'],
                    'voucher_image': item['voucher_image'][i],
                })
            return False, imgs

    def parse_table_genes(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "genes"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_genes_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['gene_code'] = row.find("./field/[@name='geneCode']").text
            item['length'] = row.find("./field/[@name='length']").text
            item['description'] = row.find("./field/[@name='description']").text
            item['reading_frame'] = row.find("./field/[@name='readingframe']").text
            item['notes'] = row.find("./field/[@name='notes']").text
            item['timestamp'] = row.find("./field/[@name='timestamp']").text
            item['genetic_code'] = row.find("./field/[@name='genetic_code']").text
            item['aligned'] = row.find("./field/[@name='aligned']").text
            item['intron'] = row.find("./field/[@name='intron']").text
            item['prot_code'] = row.find("./field/[@name='prot_code']").text
            item['genetype'] = row.find("./field/[@name='genetype']").text
            self.table_genes_items.append(item)

    def parse_table_genesets(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "genesets"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        self.table_genesets_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['geneset_name'] = row.find("./field/[@name='geneset_name']").text
            item['geneset_creator'] = row.find("./field/[@name='geneset_creator']").text
            item['geneset_description'] = row.find("./field/[@name='geneset_description']").text
            item['geneset_list'] = row.find("./field/[@name='geneset_list']").text
            # item['geneset_id'] = row.find("./field/[@name='geneset_id']").text

            if item['geneset_creator'] is None:
                item['geneset_creator'] = 'dummy'
            self.table_genesets_items.append(item)

    def parse_table_members(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "members"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_members_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['username'] = row.find("./field/[@name='login']").text
            item['first_name'] = row.find("./field/[@name='firstname']").text
            item['last_name'] = row.find("./field/[@name='lastname']").text
            item['password'] = row.find("./field/[@name='passwd']").text
            admin = str(row.find("./field/[@name='admin']").text)

            if admin == '0':
                item['is_superuser'] = False
            else:
                item['is_superuser'] = True
            item['is_staff'] = True
            item['is_active'] = True
            self.table_members_items.append(item)

    def parse_table_primers(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "primers"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_primers_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['code'] = row.find("./field/[@name='code']").text
            item['gene_code'] = row.find("./field/[@name='geneCode']").text

            item['primers'] = []
            append = item['primers'].append
            primer1 = row.find("./field/[@name='primer1']").text
            primer2 = row.find("./field/[@name='primer2']").text
            primer3 = row.find("./field/[@name='primer3']").text
            primer4 = row.find("./field/[@name='primer4']").text
            primer5 = row.find("./field/[@name='primer5']").text
            primer6 = row.find("./field/[@name='primer6']").text

            append((primer1, primer2))
            append((primer3, primer4))
            append((primer5, primer6))

            self.table_primers_items.append(item)

    def parse_table_sequences(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "sequences"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_sequences_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['code_id'] = row.find("./field/[@name='code']").text
            item['gene_code'] = row.find("./field/[@name='geneCode']").text
            try:
                item['sequences'] = row.find("./field/[@name='sequences']").text
            except AttributeError:
                item['sequences'] = ""
            item['accession'] = row.find("./field/[@name='accession']").text
            item['lab_person'] = row.find("./field/[@name='labPerson']").text
            item['time_created'] = row.find("./field/[@name='dateCreation']").text
            item['time_edited'] = row.find("./field/[@name='dateModification']").text
            try:
                item['notes'] = row.find("./field/[@name='notes']").text
            except AttributeError:
                item['notes'] = ""
            item['genbank'] = row.find("./field/[@name='genbank']").text
            self.table_sequences_items.append(item)

    def parse_table_taxonsets(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "taxonsets"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_taxonsets_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['taxonset_name'] = row.find("./field/[@name='taxonset_name']").text
            item['taxonset_creator'] = row.find("./field/[@name='taxonset_creator']").text
            item['taxonset_description'] = row.find("./field/[@name='taxonset_description']").text
            item['taxonset_list'] = row.find("./field/[@name='taxonset_list']").text
            # item['taxonset_id'] = row.find("./field/[@name='taxonset_id']").text
            self.table_taxonsets_items.append(item)

    def parse_table_vouchers(self, xml_string):
        our_data = False
        this_table = "{}vouchers".format(self.tables_prefix)

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if not our_data:
            raise ValueError("Could not find table {} in database dump file.".format(this_table))

        self.table_vouchers_items = []
        for row in our_data.findall('row'):
            item = dict()
            code = row.find("./field/[@name='code']").text
            orden = row.find("./field/[@name='orden']").text

            if code:
                item['code'] = code.strip()
            else:
                item['code'] = None

            if orden:
                item['orden'] = orden.replace('NULL', '').strip()
            else:
                item['orden'] = None

            try:
                item['superfamily'] = row.find("./field/[@name='superfamily']").text
            except AttributeError:
                item['superfamily'] = ''

            item['family'] = row.find("./field/[@name='family']").text
            item['subfamily'] = row.find("./field/[@name='subfamily']").text
            item['tribe'] = row.find("./field/[@name='tribe']").text
            item['subtribe'] = row.find("./field/[@name='subtribe']").text
            item['genus'] = row.find("./field/[@name='genus']").text
            item['species'] = row.find("./field/[@name='species']").text
            item['subspecies'] = row.find("./field/[@name='subspecies']").text
            item['country'] = row.find("./field/[@name='country']").text
            item['specific_locality'] = row.find("./field/[@name='specificLocality']").text
            item['type_species'] = row.find("./field/[@name='typeSpecies']").text
            item['latitude'] = row.find("./field/[@name='latitude']").text
            item['longitude'] = row.find("./field/[@name='longitude']").text
            item['altitude'] = row.find("./field/[@name='altitude']").text
            item['collector'] = row.find("./field/[@name='collector']").text
            item['date_collection'] = row.find("./field/[@name='dateCollection']").text
            item['voucher_image'] = row.find("./field/[@name='voucherImage']").text
            item['thumbnail'] = row.find("./field/[@name='thumbnail']").text
            item['extraction'] = row.find("./field/[@name='extraction']").text
            item['date_extraction'] = row.find("./field/[@name='dateExtraction']").text
            item['extractor'] = row.find("./field/[@name='extractor']").text
            item['voucher_locality'] = row.find("./field/[@name='voucherLocality']").text
            item['published_in'] = row.find("./field/[@name='publishedIn']").text
            item['notes'] = row.find("./field/[@name='notes']").text

            try:
                item['edits'] = row.find("./field/[@name='edits']").text
            except AttributeError:
                item['edits'] = None
            item['latest_editor'] = row.find("./field/[@name='latesteditor']").text
            try:
                item['hostorg'] = row.find("./field/[@name='hostorg']").text
            except AttributeError:
                item['hostorg'] = None
            item['sex'] = row.find("./field/[@name='sex']").text
            item['extraction_tube'] = row.find("./field/[@name='extractionTube']").text
            item['voucher'] = row.find("./field/[@name='voucher']").text
            item['voucher_code'] = row.find("./field/[@name='voucherCode']").text
            try:
                item['code_bold'] = row.find("./field/[@name='code_bold']").text
            except AttributeError:
                item['code_bold'] = None
            item['flickr_id'] = row.find("./field/[@name='flickr_id']").text
            try:
                item['determined_by'] = row.find("./field/[@name='determinedBy']").text
            except AttributeError:
                item['determined_by'] = None
            try:
                item['author'] = row.find("./field/[@name='auctor']").text
            except AttributeError:
                item['author'] = None
            item['created'] = row.find("./field/[@name='timestamp']").text
            if not item['date_collection']:
                item['date_collection'] = ""
            self.table_vouchers_items.append(item)

    def import_table_genes(self):
        if self.table_genes_items is None:
            self.parse_table_genes(self.dump_string)

        for item in self.table_genes_items:
            date_obj = self.parse_timestamp(item['timestamp'], 'timestamp')

            item['time_created'] = date_obj
            del item['timestamp']

            if item['length'] is not None:
                item['length'] = int(item['length'])

            if item['reading_frame'] is not None:
                item['reading_frame'] = int(item['reading_frame'])

            if item['aligned'] is None:
                item['aligned'] = ''

            if item['prot_code'] is None:
                item['prot_code'] = 'notset'

            item['gene_type'] = item['genetype']
            del item['genetype']

    def import_table_genesets(self):
        if self.table_genesets_items is None:
            self.parse_table_genesets(self.dump_string)

    def import_table_members(self):
        if self.table_members_items is None:
            self.parse_table_members(self.dump_string)

    def import_table_primers(self):
        if self.table_primers_items is None:
            self.parse_table_primers(self.dump_string)

        for item in self.table_primers_items:
            item['primers'] = [(i[0], i[1]) for i in item['primers'] if i[0] is not None and i[1] is not None]

    def import_table_sequences(self):
        if self.table_sequences_items is None:
            self.parse_table_sequences(self.dump_string)

        for item in self.table_sequences_items:
            item['time_created'] = self.parse_timestamp(item['time_created'], 'time_created')
            item['time_edited'] = self.parse_timestamp(item['time_edited'], 'time_edited')

            if item['sequences'] is not None:
                ambiguous_chars = item['sequences'].count('?') + item['sequences'].count('-')
                ambiguous_chars += item['sequences'].count('N') + item['sequences'].count('n')
                item['number_ambiguous_bp'] = ambiguous_chars
                item['total_number_bp'] = len(item['sequences'])
            else:
                item['number_ambiguous_bp'] = None
                item['total_number_bp'] = None

            if item['genbank'] == '0':
                item['genbank'] = False
            elif item['genbank'] == '1':
                item['genbank'] = True
            elif item['genbank'] is None:
                item['genbank'] = False
            else:
                item['genbank'] = False

    def import_table_taxonsets(self):
        if self.table_taxonsets_items is None:
            self.parse_table_taxonsets(self.dump_string)

        for item in self.table_taxonsets_items:
            if item['taxonset_description'] is None:
                item['taxonset_description'] = ''
            if item['taxonset_creator'] is None:
                item['taxonset_creator'] = ''
            if item['taxonset_list'] is not None:
                item['taxonset_list'] = item['taxonset_list'].replace(',', '\n')

    def import_table_vouchers(self):
        if self.table_vouchers_items is None:
            self.parse_table_vouchers(self.dump_string)

        self.table_flickr_images_items = []
        for item in self.table_vouchers_items:
            if item['altitude'] is not None:
                altitude = re.sub("\s+", "", item['altitude'])
                altitude = altitude.split("-")
                altitude_int = []
                for i in altitude:
                    i = re.sub("[a-zA-Z]", "", i)
                    try:
                        i = int(i)
                    except ValueError:
                        continue
                    altitude_int.append(i)
                altitude_int.sort()

                if altitude_int:
                    max_altitude = altitude_int[-1]
                    min_altitude = altitude_int[0]
                else:
                    max_altitude = None
                    min_altitude = None

                item['max_altitude'] = max_altitude
                item['min_altitude'] = min_altitude
            else:
                item['max_altitude'] = None
                item['min_altitude'] = None
            del item['altitude']

            if item['latitude'] is not None and item['latitude'] != "NULL":
                item['latitude'] = float(item['latitude'])
            if item['longitude'] is not None and item['longitude'] != "NULL":
                item['longitude'] = float(item['longitude'])

            item['date_collection'] = self.parse_collection_date(
                item['date_collection'],
                'date_collection',
            )
            item['date_extraction'] = self.parse_date(
                item['date_extraction'],
                'date_extraction',
            )
            item['created'] = self.parse_timestamp(item['created'], 'created')

            is_flickr, image_info = self.parse_image_info(item)
            if is_flickr is True:
                self.table_flickr_images_items += image_info
            if is_flickr is False:
                self.table_local_images_items += image_info

            del item['voucher_image']
            del item['thumbnail']
            if 'flickr_id' in item:
                del item['flickr_id']

            item['sex'] = get_sex(item['sex'])
            item['voucher'] = get_voucher(item['voucher'])
            item['type_species'] = parse_type_species(item['type_species'])
            self.list_of_voucher_codes.append(item['code'])

    def save_table_genes_to_db(self):
        if self.table_genes_items is None:
            self.import_table_genes()

        for item in self.table_genes_items:
            item = self.clean_value(item, 'notes')
            item = self.clean_value(item, 'intron')
            item = self.clean_value(item, 'gene_type')
            item = self.clean_value(item, 'genetic_code')
            if item['genetic_code'] == '':
                item['genetic_code'] = None
            item = self.clean_value(item, 'description')
            gene, _ = Genes.objects.get_or_create(gene_code=item['gene_code'])
            gene.length = item['length']
            gene.description = item['description']
            gene.reading_frame = item['reading_frame']
            gene.aligned = item['aligned']
            gene.prot_code = item['prot_code']
            gene.save()

    def save_table_genesets_to_db(self):
        if self.table_genesets_items is None:
            self.import_table_genesets()

        for item in self.table_genesets_items:
            if item['geneset_description'] is None:
                item['geneset_description'] = ''
            item['geneset_list'] = item['geneset_list'].replace(',', '\n')
            GeneSets.objects.get_or_create(**item)

    def save_table_members_to_db(self):
        if self.table_members_items is None:
            self.import_table_members()

        for item in self.table_members_items:
            first_name = item["first_name"]
            last_name = item["last_name"]

            if not first_name:
                first_name = "user"
            if not last_name:
                last_name = "user"

            try:
                user = User.objects.create_user(item['username'],
                                                email=None,
                                                first_name=first_name,
                                                last_name=last_name)
                user.is_staff = True
                user.is_superuser = bool(item['is_superuser'])
                user.save()
            except IntegrityError:
                print(f"User {item['username']} already exists")

        if not TESTING:
            print("\nUploading table `public_interface_members`")

    def save_table_primers_to_db(self):
        if self.table_primers_items is None:
            self.import_table_primers()

        primers_queryset = Sequences.objects.all().values('code', 'gene__gene_code')
        primers_objs = []
        for item in self.table_primers_items:
            if {'gene__gene_code': item['gene_code'], 'code': item['code']} in primers_queryset:
                try:
                    g = Genes.objects.get(gene_code=item['gene_code'])
                    item['for_sequence'] = Sequences.objects.get(
                        code=item['code'],
                        gene=g,
                    )
                except Sequences.MultipleObjectsReturned:
                    print("Multiple sequences for {} {}".format(
                        item['code'],
                        item['gene_code'],
                    ))
                    continue
            else:
                print("Could not save primers for sequence: {0} {1}".format(item['code'], item['gene_code']))
                continue

            primers = item['primers']
            del item['primers']
            del item['code']
            del item['gene_code']
            for i in primers:
                item['primer_f'] = i[0]
                item['primer_r'] = i[1]
                primers_objs.append(Primers(**item))

        for item in primers_objs:
            item.save()

        if not TESTING:
            print("\nUploading table `public_interface_primers`")

    def save_table_sequences_to_db(self):
        if self.table_sequences_items is None:
            self.import_table_sequences()

        seqs_to_insert = []
        seqs_not_to_insert = []
        seqs_invalid = []
        for i in self.table_sequences_items:
            validation = validate_sequence(i['sequences'])
            if not validation.is_valid:
                ProblematicSequence = namedtuple('ProblematicSequence',
                                                 ['code', 'gene_code', 'invalid_character'])
                prob_seq = ProblematicSequence(i['code_id'], i['gene_code'], validation.invalid_character)
                seqs_invalid.append(prob_seq)
                continue

            if i['code_id'] in self.list_of_voucher_codes:
                seqs_to_insert.append(i)
            else:
                seqs_not_to_insert.append(i)

        if not TESTING:
            print("\nUploading table `public_interface_sequences`")

        n = len(seqs_to_insert)
        if not TESTING:
            bar = pyprind.ProgBar(n, width=70)

        seqs_objects = []
        for i in range(n):
            item = seqs_to_insert[i]
            if item['sequences'] is None:
                continue

            item = self.clean_value(item, 'lab_person')
            item = self.clean_value(item, 'notes')
            item = self.clean_value(item, 'sequences')
            item = self.clean_value(item, 'accession')
            gene, _ = Genes.objects.get_or_create(gene_code=item['gene_code'])
            del item['gene_code']
            seq = Sequences(**item)
            seq.gene = gene
            seqs_objects.append(seq)
            if not TESTING:
                bar.update()

        if not TESTING:
            print("\nUploading table `public_interface_sequences`")

        for seq in seqs_objects:
            seq.save()

        if seqs_not_to_insert:
            print("ERROR: Couldn't insert {0} sequences due to lack of reference vouchers".format(len(seqs_not_to_insert)))
            for i in seqs_not_to_insert:
                print(i['code_id'], i['gene_code'])

        if seqs_invalid:
            if not TESTING:
                print("ERROR: Couldn't insert {} sequences due to invalid characters".format(len(seqs_invalid)))

            for i in seqs_invalid:
                if not TESTING:
                    msg = "ERROR: Sequence code={0}, gene_code={1}, problem={2}".format(i.code, i.gene_code, i.invalid_character)
                    print(msg)

    def save_table_taxonsets_to_db(self):
        if self.table_taxonsets_items is None:
            self.import_table_taxonsets()

        for item in self.table_taxonsets_items:
            TaxonSets.objects.get_or_create(**item)

    def test_if_photo_in_flickr(self, item):
        value = item['voucher_image']
        if value:
            if "flickr" in value:
                return True
        return False

    def save_table_vouchers_to_db(self):
        if self.table_vouchers_items is None:
            self.parse_table_vouchers(self.dump_string)

        if not TESTING:
            print("\nUploading table `public_interface_vouchers`")

        n = len(self.table_vouchers_items)
        if not TESTING:
            bar = pyprind.ProgBar(n, width=70)
        for i in range(n):
            item = self.table_vouchers_items[i]
            item = self.clean_value(item, 'orden')
            item = self.clean_value(item, 'superfamily')
            item = self.clean_value(item, 'family')
            item = self.clean_value(item, 'subfamily')
            item = self.clean_value(item, 'tribe')
            item = self.clean_value(item, 'subtribe')
            item = self.clean_value(item, 'genus')
            item = self.clean_value(item, 'species')
            item = self.clean_value(item, 'subspecies')
            item = self.clean_value(item, 'hostorg')
            item = self.clean_value(item, 'author')

            item = self.clean_value(item, 'country')
            item = self.clean_value(item, 'latitude')
            item = self.clean_value(item, 'longitude')
            item = self.clean_value(item, 'min_altitude')
            item = self.clean_value(item, 'max_altitude')
            item = self.clean_value(item, 'specific_locality')
            item = self.clean_value(item, 'voucher_locality')
            item = self.clean_value(item, 'collector')
            item = self.clean_value(item, 'voucher_code')
            item = self.clean_value(item, 'code_bold')
            item = self.clean_value(item, 'determined_by')
            item = self.clean_value(item, 'sex')

            item = self.clean_value(item, 'published_in')
            item = self.clean_value(item, 'notes')

            item = self.clean_value(item, 'extraction')
            item = self.clean_value(item, 'extraction_tube')
            item = self.clean_value(item, 'extractor')

            # voucher_objs.append(Vouchers(**item))
            try:
                Vouchers.objects.create(**item)
            except ValueError as e:
                print("Error {}".format(e))
                for key, value in item.items():
                    print(key, value, type(value))
                sys.exit(1)
            except IntegrityError:
                print(f"voucher already exists {item}")

            if not TESTING:
                bar.update()

        flickr_objs = []
        for item in self.table_flickr_images_items:
            flickr_objs.append(FlickrImages(**item))
        FlickrImages.objects.bulk_create(flickr_objs)

        image_objs = []
        for item in self.table_local_images_items:
            image_objs.append(LocalImages(**item))

        for item in image_objs:
            item.save()

        if not TESTING:
            print("\nUploading table `public_interface_flickrimages`")

    def clean_value(self, item, key):
        if key in ['latitude', 'longitude']:
            try:
                item[key] = float(item[key])
                return item
            except (TypeError, ValueError):
                item[key] = None
                return item
        if key in ['max_altitude', 'min_altitude']:
            try:
                item[key] = int(item[key])
                return item
            except (TypeError, ValueError):
                item[key] = None
                return item
        if key in item:
            if item[key] is None:
                item[key] = ''
            elif item[key].lower().strip() == 'null':
                item[key] = ''
            elif item[key].strip() == '':
                item[key] = ''
            else:
                item[key] = item[key].strip()
        else:
            item[key] = ''
        return item

    def convert_to_int(self, string):
        try:
            string = int(string)
        except TypeError:
            string = None
        except ValueError:
            string = None
        return string

    def parse_collection_date(self, mydate, field):
        try:
            date_obj = datetime.datetime.strptime(
                mydate,
                '%Y-%m-%d',
            ).replace(tzinfo=TZINFO)
        except ValueError:
            date_obj = None
        except TypeError:
            date_obj = None

        if date_obj:
            return date_obj.strftime("%Y-%m-%d")
        elif self.verbosity > 1 and not date_obj:
            print("WARNING:: Could not parse {} properly.".format(field))
            return ""
        else:
            return ""

    def parse_date(self, mydate, field):
        try:
            date_obj = datetime.datetime.strptime(mydate, '%Y-%m-%d').replace(tzinfo=TZINFO)
        except ValueError:
            date_obj = None
        except TypeError:
            date_obj = None

        if self.verbosity > 1 and not date_obj:
            print("WARNING:: Could not parse {} properly.".format(field))
        return date_obj

    def parse_timestamp(self, timestamp, field):
        try:
            date_obj = datetime.datetime.strptime(timestamp,
                                                  '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZINFO)
        except ValueError:
            date_obj = None
        except TypeError:
            date_obj = None

        if self.verbosity > 1:
            print("WARNING:: Could not parse {} properly.".format(field))
        return date_obj


def get_voucher(value):
    try:
        value = value.lower().strip()
    except AttributeError:
        return 'unknown'
    if value == 'no photo':
        return 'in envelope'
    elif value == 'no voucher':
        return 'no voucher'
    elif value == 'spread':
        return 'spread'
    elif value == 'unspread':
        return 'in envelope'
    elif value == 'voucher destroyed':
        return 'destroyed'
    elif value == 'voucher lost':
        return 'lost'
    elif value == 'voucher photo':
        return 'only photo'
    else:
        return 'unknown'


def get_sex(value):
    try:
        value = value.lower().strip()
    except AttributeError:
        return 'unknown'

    if value in ['f', 'female']:
        return 'female'
    elif value in ['m', 'male', 'mae']:
        return 'male'
    elif value == 'larva':
        return 'larva'
    elif value == 'worker':
        return 'worker'
    elif value == 'queen':
        return 'queen'
    else:
        return 'unknown'


def parse_type_species(value):
    if value == '0':
        new_value = 'unknown'
    elif value == '1':
        new_value = 'yes'
    elif value == '2':
        new_value = 'not'
    else:
        new_value = 'unknown'
    return new_value


def validate_sequence(value):
    Validation = namedtuple('Validation', ['is_valid', 'invalid_character'])

    valid_letters = set(IUPAC.ambiguous_dna.letters.upper() + 'N?-')
    sequence = value
    if sequence is None:
        validation = Validation(False, 'Empty sequence')
        return validation

    for nucleotide in sequence:
        if nucleotide == ' ':
            validation = Validation(False, 'White space')
            return validation
        if not valid_letters.issuperset(nucleotide.upper()):
            validation = Validation(False, nucleotide)
            return validation

    validation = Validation(True, '')
    return validation
    
    
def get_as_tuple(string, got_flickr=None):
    # http://www.nymphalidae.net/VoSeq/pictures/kitten1.jpg
    as_tupple = ()
    if string == 'na.gif':
        return None
    try:
        list1 = string.split("|")
    except AttributeError:
        list1 = []
    for item in list1:
        if item.strip() != '':
            item = strip_domain_from_filename(item, got_flickr)
            as_tupple += (item,)
    return as_tupple


def strip_domain_from_filename(item, got_flickr=None):
    if not got_flickr:
        disassembled = parse.urlsplit(item)
        return basename(disassembled.path)
    elif got_flickr:
        return item
    else:
        return None

