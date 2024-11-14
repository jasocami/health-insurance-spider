# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import OperarmeRecord as Record

MAIN_DOMAIN = 'https://www.operarme.es/nuestros-precios/'


class OperarmeScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get all cities list https://www.operarme.es/nuestros-precios/
    2. Get specialities list & services https://www.operarme.es/nuestros-precios/barcelona/
    3. Optional: Doctors list https://www.operarme.es/nuestros-precios/seleccionar-medico/4/barcelona/
    4. Get service
    4.1 type a : https://www.operarme.es/precio-servicio-medico/810/5-sesiones-rehabilitacion-menisco/a-coruna/
    4.2 type b : https://www.operarme.es/nuestro-precio/94/operacion-de-hemorroides/barcelona/
    4.3 type c : https://www.operarme.es/tratamiento/110/biocord-proficiency/
    4.4 type d : https://www.operarme.es/nuestro-precio/1091/cirugia-de-endoscopia-nasosinusal-unilateral-sinusitis-polipos/a-coruna/
    """

    name = 'operarme'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        """
        1. Get cities
        """
        print('PARSE START')

        cities_options = response.css('#provinces-selector a')

        for option in cities_options:
            city_href = option.attrib['href']
            city_name = option.css('::text').get().replace('\n', '').strip()
            print('Parse city {}'.format(city_name))
            kwargs['city_name'] = city_name
            yield scrapy.Request(
                url=city_href,
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        2. Get specialities
        """

        print('Parse specialities page')

        specialities_options = response.css('#wrapper .list-offers-new .collapse-item')

        city_name = kwargs['city_name']

        for option in specialities_options:
            spe_name = option.css('.collapse-item-header .collapse-item-title::text').get().replace('\n', '').strip()
            kwargs['speciality_name'] = spe_name

            services_options = option.css('.collapse-item-body > .item')

            for service in services_options:
                href = service.css('.item-link').attrib['href']
                print('Parse specialities for city {}, speciality {}'.format(city_name, spe_name))

                yield scrapy.Request(
                    url=href,
                    callback=self.__parse_service,
                    cb_kwargs=kwargs
                )

    def __parse_pre_service(self, response, **kwargs):
        """
        3. OPTIONAL - get doctors
        """

        print('Parse pre service start {}'.format(response.request.url))

        items = response.css('#list-collaborators .inner .col .inner')
        for item in items:
            href = item.css('a').attrib['href']
            yield scrapy.Request(
                url=href,
                callback=self.__parse_service,
                cb_kwargs=kwargs
            )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """
        if len(response.css('#list-collaborators .inner .col .inner')) > 0:
            # Choose doctor first
            yield scrapy.Request(
                url=response.request.url,
                callback=self.__parse_pre_service,
                cb_kwargs=kwargs,
                dont_filter=True
            )
            return

        print('Parse service start {}'.format(response.request.url))

        product_name = response.css('.detail .top .inner .right #title').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        pvp_full = response.css('.detail .top .inner .right .content-summary-price .price .bottom')
        if pvp_full:
            pvp_full = pvp_full[0].get()
            pvp_full = pvp_full.lower().replace('\n', '').strip()
            pvp_full = BeautifulSoup(pvp_full, "lxml").text  # .replace(' ', '')
            pvp_full = self.re_get_price(pvp_full)
        else:
            pvp_full = ''

        pvp = ''

        description = response.css('.detail .top .inner .right .summary').get()
        if not description or (description and 'summary-item' in description):
            description = response.css('#offer .content .detail .description').get()
        if not description:
            description = response.css('#medical-check .inner .detail .left').get()
        if not description:
            description = response.css('#wrapper .content.offer-description .description').get()
        description = BeautifulSoup(description.replace('<br>', '\n'), "lxml").text.strip()
        description = self.re_replace_multi_jump_line(description)[:1200] + '...'

        speciality = kwargs['speciality_name']

        address, center_name, health_registration = '', '', ''

        center_name = response.css('#banner-medical-check-offer #content-banner-center .right .center::text').get()
        if center_name:
            center_name = center_name.replace('\n', '').strip()
        address_list = response.css('#banner-medical-check-offer #content-banner-center .right .direccion')
        for ad in address_list:
            op = ad.get().replace('\n', '').strip()
            op = BeautifulSoup(op, "lxml").text.strip()
            if 'registro sanitario:' in op:
                health_registration = op.split(':')[1]
            else:
                address = op
        try:
            if not center_name:
                center = response.css('#wrapper > .content.file-detail.summary')[1]
                center_name = center.css('.right .name h4::text').get()
                health_registration = center.css('.right .name .number span::text').get()
                address = ''  # In description
        except:
            pass

        if not center_name:
            centers = response.css('#banner-medical-check-offer #content-banner-center .item-wrapper-selector .item-center')
            center_name = []
            address = []
            for item in centers:
                name = item.css('.right .name').get()
                name = BeautifulSoup(name, "lxml").text
                ad = item.css('.right .direccion').get()
                ad = BeautifulSoup(ad, "lxml").text
                if ad not in address:
                    center_name.append(name)
                    address.append(ad)
            center_name = '|'.join(center_name)
            address = '|'.join(address)

        includes = response.css('#banner-medical-check-offer #content-banner-includes li')
        if not includes:
            includes = response.css('#wrapper .content.offer-content .inner .offer-content-item')
        if not includes:
            includes = response.css('#wrapper .content.offer-features .inner .col li')
        if includes:
            includes_final = []
            for include in includes:
                a = include.get()
                a = BeautifulSoup(a.replace('<br>', '\n').replace('<li>', '\n'), "lxml").text
                includes_final.append(self.re_replace_multi_jump_line(a).strip())
            includes = '|'.join(includes_final)

        try:
            obj, created = Record.objects.update_or_create(
                product_name=product_name,
                speciality_name=speciality,
                center=center_name,
                city=kwargs['city_name'],
                url=response.request.url,
                defaults={
                    'pvp': pvp,
                    'includes': includes,
                    'excludes': '',
                    'pvp_full': pvp_full,
                    'description': description,
                    'address': address,
                    'health_registration': health_registration,
                    'latitude': '',
                    'longitude': '',
                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(response.request.url, e))

    def get_main_domain(self):
        return MAIN_DOMAIN
