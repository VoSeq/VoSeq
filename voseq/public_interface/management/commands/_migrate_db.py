#!-*- encoding: utf-8 -*-
"""
Needs an XML file with the database dump from MySQL:

> mysqldump --xml database > dump.xml
"""
import datetime
import pytz
import re
import xml.etree.ElementTree as ET

import pyprind
from django.conf import settings

from public_interface.models import Vouchers
from public_interface.models import FlickrImages
from public_interface.models import Sequences
from public_interface.models import Primers
from public_interface.models import Genes
from public_interface.models import GeneSets
from public_interface.models import TaxonSets


TZINFO = pytz.utc

if settings.TESTING is True:
    TESTING = True
else:
    TESTING = False


class ParseXML(object):
    """
    Parses MySQL dump as XML file.
    """
    def __init__(self, xml_string, tables_prefix=None, verbosity=None):
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
        self.list_of_voucher_codes = []
        self.verbosity = int(verbosity)

    def parse_table_genes(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "genes"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

        self.table_genes_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['geneCode'] = row.find("./field/[@name='geneCode']").text
            item['length'] = row.find("./field/[@name='length']").text
            item['description'] = row.find("./field/[@name='description']").text
            item['readingframe'] = row.find("./field/[@name='readingframe']").text
            item['notes'] = row.find("./field/[@name='notes']").text
            item['timestamp'] = row.find("./field/[@name='timestamp']").text
            item['genetic_code'] = row.find("./field/[@name='genetic_code']").text
            item['aligned'] = row.find("./field/[@name='aligned']").text
            item['intron'] = row.find("./field/[@name='intron']").text
            item['prot_code'] = row.find("./field/[@name='prot_code']").text
            item['genetype'] = row.find("./field/[@name='genetype']").text
            self.table_genes_items.append(item)

    def import_table_genes(self):
        if self.table_genes_items is None:
            self.parse_table_genes(self.dump_string)

        for item in self.table_genes_items:
            date_obj = self.parse_timestamp(item['timestamp'], 'timestamp')

            item['time_created'] = date_obj
            del item['timestamp']
            item['gene_code'] = item['geneCode']
            del item['geneCode']

            if item['length'] is not None:
                item['length'] = int(item['length'])

            if item['readingframe'] is not None:
                item['reading_frame'] = int(item['readingframe'])
            del item['readingframe']

            item['gene_type'] = item['genetype']
            del item['genetype']

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
            Genes.objects.create(**item)

    def parse_table_genesets(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "genesets"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

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

    def import_table_genesets(self):
        if self.table_genesets_items is None:
            self.parse_table_genesets(self.dump_string)

    def save_table_genesets_to_db(self):
        if self.table_genesets_items is None:
            self.import_table_genesets()

        for item in self.table_genesets_items:
            if item['geneset_description'] is None:
                item['geneset_description'] = ''
            item['geneset_list'] = item['geneset_list'].split(',')
            GeneSets.objects.create(**item)

    def parse_table_members(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "members"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

        self.table_members_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['member_id'] = row.find("./field/[@name='member_id']").text
            item['firstname'] = row.find("./field/[@name='firstname']").text
            item['lastname'] = row.find("./field/[@name='lastname']").text
            item['login'] = row.find("./field/[@name='login']").text
            item['passwd'] = row.find("./field/[@name='passwd']").text
            item['admin'] = row.find("./field/[@name='admin']").text
            self.table_members_items.append(item)

    def parse_table_primers(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "primers"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

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

    def import_table_primers(self):
        if self.table_primers_items is None:
            self.parse_table_primers(self.dump_string)

        for item in self.table_primers_items:
            item['primers'] = [(i[0], i[1]) for i in item['primers'] if i[0] is not None and i[1] is not None]

    def save_table_primers_to_db(self):
        if self.table_primers_items is None:
            self.import_table_primers()

        primers_queryset = Sequences.objects.all().values('code', 'gene_code')
        primers_objs = []
        for item in self.table_primers_items:
            if {'gene_code': item['gene_code'], 'code': item['code']} in primers_queryset:
                item['for_sequence'] = Sequences.objects.get(code=item['code'], gene_code=item['gene_code'])
            else:
                print("Could not save primers for sequence: %s %s" % (item['code'], item['gene_code']))
                continue

            primers = item['primers']
            del item['primers']
            del item['code']
            del item['gene_code']
            for i in primers:
                item['primer_f'] = i[0]
                item['primer_r'] = i[1]
                primers_objs.append(Primers(**item))
        Primers.objects.bulk_create(primers_objs)

        if self.verbosity != 0:
            print("Uploading table `public_interface_primers`")

    def parse_table_sequences(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "sequences"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

        self.table_sequences_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['code'] = row.find("./field/[@name='code']").text
            item['geneCode'] = row.find("./field/[@name='geneCode']").text
            item['sequences'] = row.find("./field/[@name='sequences']").text
            item['accession'] = row.find("./field/[@name='accession']").text
            item['labPerson'] = row.find("./field/[@name='labPerson']").text
            item['dateCreation'] = row.find("./field/[@name='dateCreation']").text
            item['dateModification'] = row.find("./field/[@name='dateModification']").text
            item['notes'] = row.find("./field/[@name='notes']").text
            item['genbank'] = row.find("./field/[@name='genbank']").text
            item['timestamp'] = row.find("./field/[@name='timestamp']").text
            self.table_sequences_items.append(item)

    def import_table_sequences(self):
        if self.table_sequences_items is None:
            self.parse_table_sequences(self.dump_string)

        for item in self.table_sequences_items:
            item['code_id'] = item['code']
            del item['code']

            item['time_created'] = item['dateCreation']
            del item['dateCreation']

            item['time_edited'] = item['dateModification']
            del item['dateModification']
            del item['timestamp']

            item['gene_code'] = item['geneCode']
            del item['geneCode']

            item['time_created'] = self.parse_timestamp(item['time_created'], 'time_created')
            item['time_edited'] = self.parse_timestamp(item['time_edited'], 'time_edited')

            if item['sequences'] is not None:
                ambiguous_chars = item['sequences'].count('?') + item['sequences'].count('-')
                ambiguous_chars += item['sequences'].count('N') + item['sequences'].count('n')
                item['number_ambiguous_bp'] = ambiguous_chars
            else:
                item['number_ambiguous_bp'] = None

            if item['genbank'] == '0':
                item['genbank'] = False
            elif item['genbank'] == '1':
                item['genbank'] = True
            elif item['genbank'] is None:
                item['genbank'] = False
            else:
                item['genbank'] = False

    def save_table_sequences_to_db(self):
        if self.table_sequences_items is None:
            self.import_table_sequences()

        seqs_to_insert = []
        seqs_not_to_insert = []
        for i in self.table_sequences_items:
            if i['code_id'] in self.list_of_voucher_codes:
                seqs_to_insert.append(i)
            else:
                seqs_not_to_insert.append(i)

        print("Uploading table `public_interface_sequences`")
        n = len(seqs_to_insert)
        if TESTING is False:
            bar = pyprind.ProgBar(n, width=70)

        seqs_objects = []
        for i in range(n):
            item = seqs_to_insert[i]
            item = self.clean_value(item, 'labPerson')
            item = self.clean_value(item, 'notes')
            item = self.clean_value(item, 'sequences')
            item = self.clean_value(item, 'accession')
            seqs_objects.append(Sequences(**item))
            if TESTING is False:
                bar.update()

        if self.verbosity != 0:
            print("Uploading table `public_interface_sequences`")
        Sequences.objects.bulk_create(seqs_objects)

        if len(seqs_not_to_insert) > 0:
            if self.verbosity != 0:
                print("Couldn't insert %i sequences due to lack of reference vouchers" % len(seqs_not_to_insert))
            for i in seqs_not_to_insert:
                if self.verbosity != 0:
                    print(i['code_id'], i['gene_code'])

    def parse_table_taxonsets(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "taxonsets"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

        self.table_taxonsets_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['taxonset_name'] = row.find("./field/[@name='taxonset_name']").text
            item['taxonset_creator'] = row.find("./field/[@name='taxonset_creator']").text
            item['taxonset_description'] = row.find("./field/[@name='taxonset_description']").text
            item['taxonset_list'] = row.find("./field/[@name='taxonset_list']").text
            # item['taxonset_id'] = row.find("./field/[@name='taxonset_id']").text
            self.table_taxonsets_items.append(item)

    def import_table_taxonsets(self):
        if self.table_taxonsets_items is None:
            self.parse_table_taxonsets(self.dump_string)

        for item in self.table_taxonsets_items:
            if item['taxonset_description'] is None:
                item['taxonset_description'] = ''
            if item['taxonset_creator'] is None:
                item['taxonset_creator'] = ''
            if item['taxonset_list'] is not None:
                item['taxonset_list'] = item['taxonset_list'].split(',')

    def save_table_taxonsets_to_db(self):
        if self.table_taxonsets_items is None:
            self.import_table_taxonsets()

        for item in self.table_taxonsets_items:
            TaxonSets.objects.create(**item)

    def parse_table_vouchers(self, xml_string):
        our_data = False
        this_table = self.tables_prefix + "vouchers"

        root = ET.fromstring(xml_string)
        for i in root.iter('table_data'):
            if i.attrib['name'] == this_table:
                our_data = i
                break

        if our_data is False:
            raise ValueError("Could not find table %s in database dump file." % this_table)

        self.table_vouchers_items = []
        for row in our_data.findall('row'):
            item = dict()
            item['code'] = row.find("./field/[@name='code']").text
            item['orden'] = row.find("./field/[@name='orden']").text
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
            item['specificLocality'] = row.find("./field/[@name='specificLocality']").text
            item['typeSpecies'] = row.find("./field/[@name='typeSpecies']").text
            item['latitude'] = row.find("./field/[@name='latitude']").text
            item['longitude'] = row.find("./field/[@name='longitude']").text
            item['altitude'] = row.find("./field/[@name='altitude']").text
            item['collector'] = row.find("./field/[@name='collector']").text
            item['dateCollection'] = row.find("./field/[@name='dateCollection']").text
            item['voucherImage'] = row.find("./field/[@name='voucherImage']").text
            item['thumbnail'] = row.find("./field/[@name='thumbnail']").text
            item['extraction'] = row.find("./field/[@name='extraction']").text
            item['dateExtraction'] = row.find("./field/[@name='dateExtraction']").text
            item['extractor'] = row.find("./field/[@name='extractor']").text
            item['voucherLocality'] = row.find("./field/[@name='voucherLocality']").text
            item['publishedIn'] = row.find("./field/[@name='publishedIn']").text
            item['notes'] = row.find("./field/[@name='notes']").text
            item['edits'] = row.find("./field/[@name='edits']").text
            item['latesteditor'] = row.find("./field/[@name='latesteditor']").text
            item['hostorg'] = row.find("./field/[@name='hostorg']").text
            item['sex'] = row.find("./field/[@name='sex']").text
            item['extractionTube'] = row.find("./field/[@name='extractionTube']").text
            item['voucher'] = row.find("./field/[@name='voucher']").text
            item['voucherCode'] = row.find("./field/[@name='voucherCode']").text
            item['flickr_id'] = row.find("./field/[@name='flickr_id']").text
            item['determinedBy'] = row.find("./field/[@name='determinedBy']").text
            item['author'] = row.find("./field/[@name='auctor']").text
            item['timestamp'] = row.find("./field/[@name='timestamp']").text
            self.table_vouchers_items.append(item)

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

                if len(altitude_int) > 0:
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

            if item['latitude'] is not None:
                item['latitude'] = float(item['latitude'])
            if item['longitude'] is not None:
                item['longitude'] = float(item['longitude'])

            item['dateCollection'] = self.parse_timestamp(item['dateCollection'], 'dateCollection')
            item['dateExtraction'] = self.parse_timestamp(item['dateExtraction'], 'dateExtraction')
            item['timestamp'] = self.parse_timestamp(item['timestamp'], 'timestamp')

            # Deal with flickr images
            if item['voucherImage'] == '':
                item['voucherImage'] = None
            elif item['voucherImage'] is not None:
                item['voucherImage'] = self.get_as_tuple(item['voucherImage'])

            if item['thumbnail'] == '':
                item['thumbnail'] = None
            elif item['thumbnail'] is not None:
                item['thumbnail'] = self.get_as_tuple(item['thumbnail'])

            if item['flickr_id'] == '':
                item['flickr_id'] = None
            elif item['flickr_id'] is not None:
                item['flickr_id'] = self.get_as_tuple(item['flickr_id'])

            items_to_flickr = None
            if item['voucherImage'] is not None and item['thumbnail'] is not None \
                    and item['flickr_id'] is not None:
                items_to_flickr = []
                for i in range(0, len(item['voucherImage']), 1):
                    items_to_flickr.append({
                        'voucher_id': item['code'],
                        'voucherImage': item['voucherImage'][i],
                        'thumbnail': item['thumbnail'][i],
                        'flickr_id': item['flickr_id'][i],
                    })
            del item['voucherImage']
            del item['thumbnail']
            del item['flickr_id']

            if item['sex'] is not None:
                item['sex'] = get_sex(item['sex'])

            if item['voucher'] is not None:
                item['voucher'] = self.get_voucher(item['voucher'])
            else:
                item['voucher'] = 'n'

            item['typeSpecies'] = parse_type_species(item['typeSpecies'])

            if items_to_flickr is not None:
                self.table_flickr_images_items += items_to_flickr

            self.list_of_voucher_codes.append(item['code'])

    def save_table_vouchers_to_db(self):
        if self.table_vouchers_items is None:
            self.parse_table_vouchers(self.dump_string)

        print("Uploading table `public_interface_vouchers`")

        voucher_objs = []
        n = len(self.table_vouchers_items)
        if TESTING is False:
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
            item = self.clean_value(item, 'specificLocality')
            item = self.clean_value(item, 'voucherLocality')
            item = self.clean_value(item, 'collector')
            item = self.clean_value(item, 'voucherCode')
            item = self.clean_value(item, 'determinedBy')
            item = self.clean_value(item, 'sex')

            item = self.clean_value(item, 'publishedIn')
            item = self.clean_value(item, 'notes')

            item = self.clean_value(item, 'extraction')
            item = self.clean_value(item, 'extractionTube')
            item = self.clean_value(item, 'extractor')

            voucher_objs.append(Vouchers(**item))

            if TESTING is False:
                bar.update()
        Vouchers.objects.bulk_create(voucher_objs)

        flickr_objs = []
        for item in self.table_flickr_images_items:
            flickr_objs.append(FlickrImages(**item))
        FlickrImages.objects.bulk_create(flickr_objs)

        if self.verbosity != 0:
            print("Uploading table `public_interface_flickrimages`")

    def clean_value(self, item, key):
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

    def get_as_tuple(self, string):
        as_tupple = ()
        if string == 'na.gif':
            return None
        list1 = string.split("|")
        for item in list1:
            if item.strip() != '':
                as_tupple += (item,)

        return as_tupple

    def get_voucher(self, string):
        string = string.lower().strip()
        if string == 'no photo':
            return 'e'
        elif string == 'no voucher':
            return 'n'
        elif string == 'spread':
            return 's'
        elif string == 'unspread':
            return 'e'
        elif string == 'voucher destroyed':
            return 'd'
        elif string == 'voucher lost':
            return 'l'
        elif string == 'voucher photo':
            return 'p'
        else:
            return 'n'

    def convert_to_int(self, string):
        try:
            string = int(string)
        except TypeError:
            string = None
        except ValueError:
            string = None
        return string

    def parse_timestamp(self, timestamp, field):
        try:
            date_obj = datetime.datetime.strptime(timestamp,
                                                  '%Y-%m-%d %H:%M:%S').replace(tzinfo=TZINFO)
        except ValueError:
            date_obj = None
        except TypeError:
            date_obj = None

        if self.verbosity != 0:
            print("WARNING:: Could not parse %s properly." % field)
        return date_obj


def get_sex(value):
    value = value.lower().strip()
    if value == 'f' or value == 'female':
        return 'f'
    elif value == 'm' or value == 'male' or value == 'mae':
        return 'm'
    else:
        return None


def parse_type_species(value):
    if value == '0':
        new_value = 'd'
    elif value == '1':
        new_value = 'y'
    elif value == '2':
        new_value = 'n'
    else:
        new_value = 'd'
    return new_value
