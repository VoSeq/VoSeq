import csv
import datetime

from django.http import HttpResponse

from public_interface.models import Vouchers


def get_data_count():
    voucher_count = Vouchers.objects.count()
    return voucher_count


def create_excel_file():
    today = datetime.date.today()
    filename = 'data_for_GBIF_' + datetime.date.strftime(today, '%Y%m%d') + '.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'

    writer = csv.writer(response)

    row = ['Code', 'Order', 'Superfamily', 'Family', 'Subfamily', 'Tribe', 'Subtribe', 'Genus',
           'Species', 'Subspecies', 'TypeSpecies', 'Country', 'Specific_Locality', 'Latitude',
           'Longitude', 'Max. Altitude', 'Min. Altitude', 'Collector', 'Date_of_Collection',
           'Voucher_Locality', 'Host_Organism', 'Sex', 'Voucher_State', 'Voucher_code_from_others',
           'Code from BOLD',
           'Date_of_DNA_extraction', 'Extractor', 'Extraction #', 'Extraction_Vial',
           'Published_in', 'Notes']

    writer.writerow(row)

    vouchers = Vouchers.objects.all()
    for voucher in vouchers:
        row = [voucher.code]
        row.append(voucher.orden)
        row.append(voucher.superfamily)
        row.append(voucher.family)
        row.append(voucher.subfamily)
        row.append(voucher.tribe)
        row.append(voucher.subtribe)
        row.append(voucher.genus)
        row.append(voucher.species)
        row.append(voucher.subspecies)
        row.append(get_type_species(voucher.typeSpecies))
        row.append(voucher.country)
        row.append(voucher.specificLocality)
        row.append(voucher.latitude)
        row.append(voucher.longitude)
        row.append(voucher.max_altitude)
        row.append(voucher.min_altitude)
        row.append(voucher.collector)
        row.append(voucher.dateCollection)
        row.append(voucher.voucherLocality)
        row.append(voucher.hostorg)
        row.append(get_sex(voucher.sex))
        row.append(get_voucher_state(voucher.voucher))
        row.append(voucher.voucherCode)
        row.append(voucher.code_bold)
        row.append(voucher.dateExtraction)
        row.append(voucher.extractor)
        row.append(voucher.extractionTube)
        row.append(voucher.publishedIn)
        row.append(voucher.notes)
        writer.writerow(row)
    return response


def get_type_species(value):
    if value == 'd':
        return 'do not know'
    elif value == 'y':
        return 'yes'
    elif value == 'n':
        return 'no'
    else:
        return ''


def get_sex(value):
    if value == 'm':
        return 'male'
    elif value == 'f':
        return 'female'
    elif value == 'l':
        return 'larva'
    elif value == 'w':
        return 'worker'
    elif value == 'q':
        return 'queen'
    elif value == 'u':
        return 'unknown'
    else:
        return ''


def get_voucher_state(value):
    if value == 's':
        return 'spread'
    elif value == 'e':
        return 'envelope'
    elif value == 'p':
        return 'photo'
    elif value == 'n':
        return 'no voucher'
    elif value == 'd':
        return 'destroyed'
    elif value == 'l':
        return 'lost'
    elif value == 'u':
        return 'unknown'
    else:
        return ''
