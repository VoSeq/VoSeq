#!-*- encoding: utf-8 -*-
"""
Needs an XML file with the database dump from MySQL:

> mysqldump --xml database > dump.xml
"""
import codecs
import datetime
import dataset
import json
import re
import sys
import xml.etree.ElementTree as ET

from public_interface.models import Vouchers
from public_interface.models import FlickrImages
from public_interface.models import Sequences
from public_interface.models import Primers


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
        self.verbosity = verbosity

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
            item['geneset_id'] = row.find("./field/[@name='geneset_id']").text
            self.table_genesets_items.append(item)

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
            item['taxonset_id'] = row.find("./field/[@name='taxonset_id']").text
            self.table_taxonsets_items.append(item)

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
            item['auctor'] = row.find("./field/[@name='auctor']").text
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

            if item['dateCollection'] is not None:
                try:
                    date_obj = datetime.datetime.strptime(item['dateCollection'], '%Y-%m-%d').date()
                except ValueError:
                    date_obj = None
                item['dateCollection'] = date_obj

            if item['dateExtraction'] is not None:
                try:
                    date_obj = datetime.datetime.strptime(item['dateExtraction'], '%Y-%m-%d').date()
                except ValueError:
                    date_obj = None
                item['dateExtraction'] = date_obj

            if item['timestamp'] is not None:
                try:
                    date_obj = datetime.datetime.strptime(item['timestamp'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    date_obj = None
                item['timestamp'] = date_obj

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
                item['sex'] = self.get_sex(item['sex'])

            if item['voucher'] is not None:
                item['voucher'] = self.get_voucher(item['voucher'])
            else:
                item['voucher'] = 'n'

            if item['typeSpecies'] == '0':
                item['typeSpecies'] = 'd'
            elif item['typeSpecies'] == '1':
                item['typeSpecies'] = 'y'
            elif item['typeSpecies'] == '2':
                item['typeSpecies'] = 'n'
            else:
                item['typeSpecies'] = 'd'

            if items_to_flickr is not None:
                self.table_flickr_images_items += items_to_flickr

            self.list_of_voucher_codes.append(item['code'])

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

            try:
                date_obj = datetime.datetime.strptime(item['time_created'], '%Y-%m-%d')
            except ValueError as e:
                date_obj = None
                if self.verbosity != 0:
                    print(e)
                    print("WARNING:: Could not parse dateCreation properly.")
                    print("WARNING:: Using empty date for `time_created` for code %s and gene_code %s." % (item['code_id'], item['gene_code']))
            except TypeError as e:
                date_obj = None
                if self.verbosity != 0:
                    print(e)
                    print("WARNING:: Could not parse dateCreation properly.")
                    print("WARNING:: Using empty date for `time_created` for code %s and gene_code %s." % (item['code_id'], item['gene_code']))

            item['time_created'] = date_obj

            try:
                date_obj = datetime.datetime.strptime(item['time_edited'], '%Y-%m-%d')
            except ValueError:
                date_obj = None
                if self.verbosity != 0:
                    print("WARNING:: Could not parse dateModification properly.")
                    print("WARNING:: Using empty date for `time_edited` for code %s." % item['code_id'])
            except TypeError:
                date_obj = None
                if self.verbosity != 0:
                    print("WARNING:: Could not parse dateCreation properly.")
                    print("WARNING:: Using empty as date for `time_edited` for code %s." % item['code_id'])

            item['time_edited'] = date_obj

    def import_table_primers(self):
        if self.table_primers_items is None:
            self.parse_table_primers(self.dump_string)

        for item in self.table_primers_items:
            item['primers'] = [(i[0], i[1]) for i in item['primers'] if i[0] is not None and i[1] is not None]

    def save_table_primers_to_db(self):
        if self.table_primers_items is None:
            self.import_table_primers()

        for item in self.table_primers_items:
            b = Sequences.objects.get(code=item['code'], gene_code=item['gene_code'])
            item['for_sequence'] = b

            primers = item['primers']
            del item['primers']
            del item['code']
            del item['gene_code']
            for i in primers:
                item['primer_f'] = i[0]
                item['primer_r'] = i[1]
                Primers.objects.create(**item)

        if self.verbosity != 0:
            print("Uploading table `public_interface_primers`")

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

    def save_table_vouchers_to_db(self):
        if self.table_vouchers_items is None:
            self.parse_table_vouchers(self.dump_string)

        for item in self.table_vouchers_items:
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
            item = self.clean_value(item, 'auctor')

            item = self.clean_value(item, 'country')
            item = self.clean_value(item, 'specificLocality')
            item = self.clean_value(item, 'voucherLocality')
            item = self.clean_value(item, 'collector')
            item = self.clean_value(item, 'voucherCode')
            item = self.clean_value(item, 'determinedBy')
            item = self.clean_value(item, 'sex')

            item = self.clean_value(item, 'publishedIn')
            item = self.clean_value(item, 'notes')

            item = self.clean_value(item, 'extractionTube')
            item = self.clean_value(item, 'extractionTube')
            item = self.clean_value(item, 'extractor')

            Vouchers.objects.create(**item)
        if self.verbosity != 0:
            print("Uploading table `public_interface_vouchers`")

        for item in self.table_flickr_images_items:
            FlickrImages.objects.create(**item)
        if self.verbosity != 0:
            print("Uploading table `public_interface_flickrimages`")

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
        for item in seqs_to_insert:
            item = self.clean_value(item, 'labPerson')
            item = self.clean_value(item, 'notes')
            item = self.clean_value(item, 'sequences')
            item = self.clean_value(item, 'accession')
            Sequences.objects.create(**item)

        if self.verbosity != 0:
            print("Uploading table `public_interface_sequences`")

        if len(seqs_not_to_insert) > 0:
            if self.verbosity != 0:
                print("Couldn't insert %i sequences due to lack of reference vouchers" % len(seqs_not_to_insert))
            for i in seqs_not_to_insert:
                if self.verbosity != 0:
                    print(i['code_id'], i['gene_code'])

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

    def get_sex(self, string):
        string = string.lower().strip()
        if string == 'f' or string == 'female':
            return 'f'
        elif string == 'm' or string == 'male' or string == 'mae':
            return 'm'
        else:
            return None

    def convert_to_int(self, string):
        try:
            string = int(string)
        except TypeError:
            string = None
        except ValueError:
            string = None
        return string


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Enter name of database dump file as argument.")
        print("This file can be obtained from your MySQL database using this command")
        print("\t> mysqdump --xml database > dump.xml")
        sys.exit(1)

    dump_file = sys.argv[1].strip()
    with codecs.open(dump_file, "r") as handle:
        dump = handle.read()

    # tables_prefix = 'voseq_'
    tables_prefix = ''
    parser = ParseXML(dump, tables_prefix)

    parser.import_table_vouchers()
    parser.save_table_vouchers_to_db()

    parser.import_table_sequences()
    parser.save_table_sequences_to_db()
