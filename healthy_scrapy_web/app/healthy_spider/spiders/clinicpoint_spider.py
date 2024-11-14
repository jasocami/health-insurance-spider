# -*- coding: utf-8 -*-
import urllib.parse
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import ClinicPointRecord


MAIN_DOMAIN = 'https://www.clinicpoint.com'


class ClinicointScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.
    1. Scrap home (https://www.clinicpoint.com)
    1.1 Get all Provinces (html)
    1.2 Get all specialities
    2. List services (https://www.clinicpoint.com/madrid/fisioterapia)
    3. Optional: List sub-services (https://www.clinicpoint.com/madrid/fisioterapia/fisioterapia)
    4. List centers (https://www.clinicpoint.com/madrid/fisioterapia/fisioterapia/1-sesion-de-fisioterapia-y-osteopatia)
    5. Get product (https://www.clinicpoint.com/madrid/offer/9310/1-sesion-de-fisioterapia-y-osteopatia)
    """

    name = 'clinicpoint'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        """
        1. Scrap home (https://www.clinicpoint.com)
        1.1 Get all Provinces (html)
        """
        print('START PARSE')
        cities_list = response.css('.navigation-city-body .navigation-city-content-city a')

        for city in cities_list:
            city_href_id = city.attrib['href'].replace('https://www.clinicpoint.com/', '').split('/')[0]
            city_name = city.css('::text').get()
            kwargs['city_href_id'] = city_href_id
            kwargs['city_name'] = city_name

            print('Parse City {}'.format(city_name))

            yield scrapy.Request(
                url=self.__get_speciality_list_url(city_href_id),
                callback=self.__parse_speciality_list,
                cb_kwargs=kwargs
            )

    def __parse_speciality_list(self, response, **kwargs):
        """
        1.2 Get all specialities
        """
        specialities_list = response.css('.navigation-li.first.navigation-all-link a')

        for speciality in specialities_list:
            speciality_href_id = speciality.attrib['href'].split('/')[-1]
            speciality_name = speciality.css('::text').get()

            city_href_id = kwargs['city_href_id']
            city_name = kwargs['city_name']

            print('Parse City {} speciality {}'.format(city_name, speciality_name))

            kwargs['speciality_href_id'] = speciality_href_id
            kwargs['speciality_name'] = speciality_name

            yield scrapy.Request(
                url=self.__get_speciality_services_url(city_href_id, speciality_href_id),
                callback=self.__parse_speciality_services,
                cb_kwargs=kwargs
            )

    def __parse_speciality_services(self, response, **kwargs):
        """
        2. List services (https://www.clinicpoint.com/madrid/fisioterapia)
        :param response:
        :return:
        """
        print('Parse speciality start {}'.format(response.request.url))

        services_list = response.css('.navigationServices .navigationServices-list a')

        for service in services_list:
            href = service.attrib['href']
            speciality_name = service.css('::text').get()
            kwargs['speciality_name1'] = speciality_name.replace('\n', '').strip()

            yield scrapy.Request(
                url=urllib.parse.urljoin(MAIN_DOMAIN, href),
                callback=self.__parse_sub_speciality_services,
                cb_kwargs=kwargs
            )

    def __parse_sub_speciality_services(self, response, **kwargs):
        """
        3. Optional: List sub-services (https://www.clinicpoint.com/madrid/fisioterapia/fisioterapia)
        :param response:
        :return:
        """
        print('Parse sub speciality start {}'.format(response.request.url))

        services_list = response.css('.navigationServices .navigationServices-list a')

        if len(services_list) == 0:
            yield scrapy.Request(
                    url=response.request.url,
                    callback=self.__parse_services,
                    cb_kwargs=kwargs,
                    dont_filter=True
                )
        else:
            for service in services_list:
                href = service.attrib['href']
                speciality_name = service.css('::text').get()
                kwargs['speciality_name2'] = speciality_name.replace('\n', '').strip()
                yield scrapy.Request(
                    url=urllib.parse.urljoin(MAIN_DOMAIN, href),
                    callback=self.__parse_services,
                    cb_kwargs=kwargs
                )

    def __parse_services(self, response, **kwargs):
        """
        4. List centers (https://www.clinicpoint.com/madrid/fisioterapia/fisioterapia/1-sesion-de-fisioterapia-y-osteopatia)
        """
        print('Parse services start {}'.format(response.request.url))

        services_list = response.css('#offersContainer #product-offers .item')

        if len(services_list) == 0:
            yield scrapy.Request(
                url=response.request.url,
                callback=self.__parse_product,
                cb_kwargs=kwargs,
                dont_filter=True
            )

        for service in services_list:
            href = service.css('.offer-button a').attrib['href']
            yield scrapy.Request(
                url=urllib.parse.urljoin(MAIN_DOMAIN, href),
                callback=self.__parse_product,
                cb_kwargs=kwargs
            )

    def __parse_product(self, response, **kwargs):
        """
        5. Get product (https://www.clinicpoint.com/madrid/offer/9310/1-sesion-de-fisioterapia-y-osteopatia)
        :param response:
        :return:
        """
        print('Parse product start {}'.format(response.request.url))
        product_name = response.css('#offerDetail h1').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        try:
            speciality = response.css('.breadcrumb li')
            l = []
            for ex in speciality[1:len(speciality)-1]:
                v = ex.css('span::text').get().replace('\n', '').strip()
                if v != '':
                    l.append(v)
            speciality = ' - '.join(l)
        except:
            speciality = ' - '.join([kwargs['speciality_name'], kwargs.get('speciality_name1', ''), kwargs.get('speciality_name2', '')])

        pvp = response.css('#offerDetail #financedTextBlock a').get().lower().replace('\n', '').strip()
        pvp = BeautifulSoup(pvp, "lxml").text.replace(' ', '')
        try:
            pvp = self.re_get_price(pvp)
        except:
            pvp = '' # pvp.replace('comprar', '').replace('reservar', '').replace('paga', '').replace('y', '').replace('de', '').strip()
        pvp_full = response.css('#offerDetail .prices-container .offer-detail--offer-price--pvpmp span::text').get().replace('€', '').strip()
        description = response.css('#offerDescription div').get()
        description = BeautifulSoup(description, "lxml").text.replace('Descripción\n', '').strip()
        center_name = response.css('.offer-detail--main-provider a.provider-link::text').get().replace('\n', '').strip()
        province = kwargs['city_name']

        try:
            includes_list = response.css('.offer-detail--offer-includes ul')[0].css('li')
            includes = '|'.join([ex.css('::text').get() for ex in includes_list])
        except:
            includes = ''

        try:
            excludes_list = response.css('.offer-detail--offer-includes ul')[1].css('li')
            excludes = '|'.join([ex.css('::text').get() for ex in excludes_list])
        except:
            excludes = ''

        address = response.css('#offerLocation address::text').get().replace('\n', '').strip()
        if address == '':
            # Example https://www.clinicpoint.com/malaga/offer/7419/test-de-chequeo-completo-para-el-hombre
            address = response.css('#offerLocation .locations-list li')
            address_list_f = []
            for item in address:
                it = item.get().replace('\n', '').strip()
                it = BeautifulSoup(it, "lxml").text.strip()
                address_list_f.append(it)
            address = '|'.join(address_list_f)

        # health_registration = response.css('#offerLocation .provider-reg-number::text').get().split(':')[-1].strip()
        # latitude = ''
        # longitude = ''

        try:
            obj, created = ClinicPointRecord.objects.update_or_create(
                product_name=product_name,
                speciality_name=speciality,
                center=center_name,
                province_name=province,
                url=response.request.url,
                defaults={
                    'description': description,
                    'pvp': pvp,
                    'address': address,
                    'pvp_full': pvp_full,
                    'latitude': '',
                    'longitude': '',
                    'includes': includes,
                    'excludes': excludes,
                    'health_registration': '',

                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print(e)
            print('Error for url {} || {}'.format(response.request.url, e))

    def __get_speciality_services_url(self, province, speciality):
        return 'https://www.clinicpoint.com/{}/{}'.format(province, speciality)

    def __get_speciality_list_url(self, province):
        return 'https://www.clinicpoint.com/{}'.format(province)
