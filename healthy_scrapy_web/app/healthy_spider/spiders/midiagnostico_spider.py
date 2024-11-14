# -*- coding: utf-8 -*-
import re
import urllib.parse
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import MiDiagnosticoRecord as Record

MAIN_DOMAIN = 'https://midiagnostico.es/'


class MiDiagnosticoScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get all provinces list (https://midiagnostico.es/ubicacion.php)
    2. Get specialities list loop (https://midiagnostico.es/pruebas/barcelona)
    4. Get service (https://midiagnostico.es/pruebas/estudios-geneticos/nutricion/analisis-nutrigenetica-sobrepeso)
    4.1 Get service does not exist https://midiagnostico.es/pruebas/barcelona/resonancia-magnetica/resonancia-magnetica-abdomen
    """

    name = 'midiagnostico'
    start_urls = [
        'https://midiagnostico.es/ubicacion.php'
    ]

    def parse(self, response, **kwargs):
        """
        1. Get provinces
        """
        print('PARSE START')

        provinces_options = response.css('nav .ciudad-contacto a')

        kwargs['speciality_name'] = {}

        for option in provinces_options:
            pro_href = option.attrib['href']
            pro_name = option.css('::text').get().replace('\n', '').strip()

            if 'contacto' in pro_name.lower() or 'otra ciudad' in pro_name.lower():
                continue

            print('Parse province {}'.format(pro_name))

            kwargs['pro_name'] = pro_name

            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), pro_href),
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        2. Get specialities
        """

        print('Parse specialities page')

        specialities_options = response.css('#contenido .dims .lista-resultados .caja-resultado')

        pro_name = kwargs['pro_name']

        if len(specialities_options) > 0 and not response.css('#contenido #descripcion-larga-prueba'):
            for option in specialities_options:
                option = option.css('.txt-caja a')
                if type(option) == list:
                    option = option[0]
                if 'href' not in option.attrib:
                    continue
                spe_href = option.attrib['href']
                spe_name = option.css('::text').get().replace('\n', '').strip()

                if spe_href.startswith('#'):
                    continue

                print('Parse specialities for province {}, speciality {}'.format(pro_name, spe_name))

                yield scrapy.Request(
                    url=spe_href,
                    callback=self.__parse_specialities_page,
                    cb_kwargs=kwargs.copy()
                )
        else:
            yield scrapy.Request(
                url=response.request.url,
                callback=self.__parse_service,
                cb_kwargs=kwargs,
                dont_filter=True
            )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """
        print('Parse service start {}'.format(response.request.url))

        if response.css('#contenido .dims .mensaje.aviso.no-disponible').get():
            return

        product_name = response.css('#contenido h1').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()
        if product_name.startswith('€'):
            product_name = product_name[1:].strip()
        province = kwargs['pro_name']

        speciality_items = response.request.url.replace(self.get_main_domain(), '').split('/')

        for item in ['pruebas', province.lower()]:
            try:
                i = speciality_items.index(item)
                speciality_items.pop(i)
            except:
                pass

        speciality = '|'.join(speciality_items[:1])

        try:
            pvp_full = response.css('#contenido .datos-precio').get().lower().replace('\n', '').strip()
            pvp_full = BeautifulSoup(pvp_full, "lxml").text.replace(' ', '')
            pvp_full = self.re_get_price(pvp_full)
        except:
            pvp_full = ''

        description = response.css('#contenido #descripcion-larga-prueba .descripciones')
        if not description:
            description = response.css('#contenido #descripcion-larga-prueba')

        description = self.re_replace_multi_jump_line(
            BeautifulSoup(description.get().replace('<br>', '\n'), "lxml").text.strip()
        )[:1200] + '...'

        includes = ''
        excludes = ''

        center_box = response.css('#contenido #datos-ms')
        if not center_box:
            center_box = response.css('#contenido #encabezado-resultados .datos-clinica')
        if not center_box:
            center_box = response.css('#contenido .lista-resultados.clinicas.cols li')
        if center_box:
            centers_list = []
            address_list = []
            for item in center_box:
                center_name = item.css('h2::text').get()
                if not center_name:
                    center_img = center_box.css('h2 img')
                    if center_img and 'alt' in center_img.attrib:
                        center_name = center_img.attrib['alt']
                else:
                    center_name = center_name.replace('\n', '').strip()
                address = center_box.css('p')[0].get().replace('\n', '').replace('\r', ' ').replace('<br>', ' ')\
                    .replace('<p>', ' ').replace('</p>', ' ').strip()
                centers_list.append(center_name)
                address_list.append(address)
            center_name = '|'.join(centers_list)
            address = '|'.join(address_list)
        else:
            center_name = ''
            address = ''

        latitude = ''
        longitude = ''

        health_registration = ''
        city = ''
        town = ''  # Not found in web

        try:
            obj, created = Record.objects.update_or_create(
                product_name=product_name,
                speciality_name=speciality,
                center=center_name,
                province_name=province,
                city=city,
                town=town,
                url=response.request.url,
                defaults={
                    'pvp': '',
                    'pvp_full': pvp_full,
                    'description': description,
                    'includes': includes,
                    'excludes': excludes,
                    'address': address,
                    'health_registration': health_registration,
                    'latitude': latitude,
                    'longitude': longitude,
                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(response.request.url, e))

    def get_main_domain(self):
        return MAIN_DOMAIN
