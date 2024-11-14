import os
import csv

from django.http import HttpResponse

from healthy_spider_records.models import ClinicPointRecord, QuironRecord, SaludonnetRecord, SmartSalusRecord, \
    IglobalmedRecord, OperarmeRecord, MiDiagnosticoRecord, BonomedicoRecord, PortalsaludSanitasRecord


class CSVDownloadView:
    """
    Clase base para la descarga de CSV
    """

    CSV_DELIMITER = ';'

    def create_tmp_dir(self):
        """
        Crea la carpeta temporal para almacenar los ficheros si no existe
        """
        csv_directory = os.environ.get('CSV_FOLDER')
        if not os.path.exists(csv_directory):
            os.mkdir(csv_directory)
        return csv_directory

    def write(self):
        """
        Esta función deben redefinirla todas las clases que hereden de esta. Es la encargada de escribir en un fichero el csv que se descargará
        """
        raise NotImplementedError('Subclasses most implement me')

    def make_response(self, filename):
        self.write()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(filename)

        csv_directory = os.environ.get('CSV_FOLDER')
        with open(os.path.join(csv_directory, '{}.csv'.format(filename)), 'r') as f:
            data = f.readlines()
            response.content = data

        os.remove(os.path.join(csv_directory, '{}.csv'.format(filename)))
        return response


class QuironRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'quiron.csv')

        records = QuironRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['tipo_producto', 'nombre_producto', 'especialidad', 'pvp', 'grupo', 'provincia', 'centro', 'descripcion', 'url', 'fecha_creacion'])

            for rec in records:
                row = [rec.type_product_name, rec.product_name, rec.speciality_name, rec.pvp, rec.group, rec.province_name, rec.center, rec.description, rec.url, rec.creation_timestamp]
                writer.writerow(row)

    def get(self, request):
        response = self.make_response('quiron')
        return response


class SaludOnNetRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'saludonnet.csv')

        records = SaludonnetRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_full', 'grupo', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.group, rec.description,
                       rec.center, rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                       rec.address, rec.health_registration, rec.url, rec.creation_timestamp]
                writer.writerow(row)

    def get(self, request):
        response = self.make_response('saludonnet')
        return response


class ClinicPointRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'clinicpoint.csv')

        records = ClinicPointRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                for address in rec.address.split('|'):
                    row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.description,
                           rec.center, rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                           address, rec.health_registration, rec.url, rec.creation_timestamp]
                    writer.writerow(row)

    def get(self, request):
        response = self.make_response('clinicpoint')
        return response


class SmartSalusRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'smartsalus.csv')

        records = SmartSalusRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.description,
                       rec.center, rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                       rec.address, rec.health_registration, rec.url, rec.creation_timestamp]
                writer.writerow(row)

    def get(self, request):
        response = self.make_response('smartsalus')
        return response


class IglobalmedRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'iglobalmed.csv')

        records = IglobalmedRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_medio', 'pvp_full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_middle, rec.pvp_full, rec.description,
                       rec.center, rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                       rec.address, rec.health_registration, rec.url, rec.creation_timestamp]
                writer.writerow(row)

    def get(self, request):
        response = self.make_response('iglobalmed')
        return response


class OperarmeRecordCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'operarme.csv')

        records = OperarmeRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:

                address_list = rec.address.split('|')
                centers_list = rec.center.split('|')
                index = 0
                for i in range(0, len(centers_list)):
                    row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.description,
                           centers_list[i], rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                           address_list[i], rec.health_registration, rec.url, rec.creation_timestamp]
                    writer.writerow(row)
                    index += 1

    def get(self, request):
        response = self.make_response('operarme')
        return response


class MiDiagnosticoRecordsCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'midiagnostico.csv')

        records = MiDiagnosticoRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                address_list = rec.address.split('|')
                centers_list = rec.center.split('|')
                for i in range(0, len(centers_list)):
                    row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.description,
                           centers_list[i], rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                           address_list[i], rec.health_registration, rec.url, rec.creation_timestamp]
                    writer.writerow(row)

    def get(self, request):
        response = self.make_response('midiagnostico')
        return response


class BonomedicoCSVDownloadView(CSVDownloadView):
    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'bonomedico.csv')

        records = BonomedicoRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp_full', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:

                product_name_list = rec.product_name.split('|')
                pvp_full_list = rec.pvp_full.split('|')
                centers_list = rec.center.split('|')
                address_list = rec.address.split('|')
                for i in range(0, len(product_name_list)):
                    product_name = product_name_list[i].strip()
                    pvp_full = pvp_full_list[i]
                    if product_name == '':
                        continue
                    for ii in range(0, len(centers_list)):
                        center = centers_list[ii].strip()
                        address = address_list[ii]
                        row = [product_name, rec.speciality_name, rec.pvp, pvp_full, rec.description,
                               center, rec.province_name, rec.city, rec.town, rec.includes, rec.excludes,
                               address, rec.health_registration, rec.url, rec.creation_timestamp]
                        writer.writerow(row)

    def get(self, request):
        response = self.make_response('bonomedico')
        return response


class PortalsaludSanitasCSVDownloadView(CSVDownloadView):

    def write(self):
        csv_directory = self.create_tmp_dir()
        path = os.path.join(csv_directory, 'portalsalud_sanitas.csv')

        records = PortalsaludSanitasRecord.objects.all()
        with open(path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, dialect='excel', delimiter=self.CSV_DELIMITER, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(['nombre_producto', 'especialidad', 'pvp', 'pvp full', 'sexo', 'descripcion',
                             'centro', 'provincia', 'ciudad', 'municipio', 'incluye', 'excluye',
                             'direccion', 'registro', 'url', 'fecha_creacion'])

            for rec in records:
                # City, town and health_registration column is empty
                address_list = rec.address.split('|')
                centers_list = rec.center.split('|')
                for i in range(0, len(centers_list)):
                    row = [rec.product_name, rec.speciality_name, rec.pvp, rec.pvp_full, rec.gender, rec.description,
                           centers_list[i], rec.province_name, '', '', rec.includes, rec.excludes,
                           address_list[i], '', rec.url, rec.creation_timestamp]
                    writer.writerow(row)

    def get(self, request):
        response = self.make_response('portalsalud_sanitas')
        return response

