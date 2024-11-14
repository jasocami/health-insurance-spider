# -*- coding: utf-8 -*-
import os
import urllib.parse
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import IglobalmedRecord as Record

MAIN_DOMAIN = 'https://www.iglobalmed.com/'


class IglobalmedScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get all provinces list (https://www.iglobalmed.com/)
    2. Get specialities list https://www.iglobalmed.com/madrid/todas_especialidades)
    3. Get services https://www.iglobalmed.com/madrid/analitica
    4. Get service https://www.iglobalmed.com/madrid/test-genetico-genosport--lesiones-en-megalab-madrid
    """

    name = 'iglobalmed'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        """
        1. Get cities
        """
        print('PARSE START')

        cities_options = response.css('#all_cities .all-cities-list a')

        for option in cities_options:
            city_href = option.attrib['href']
            city_name = option.get().replace('\n', '').strip()
            city_name = BeautifulSoup(city_name, "lxml").text.replace(' ', '').strip()

            print('Parse city {}'.format(city_name))

            kwargs['city_name'] = city_name
            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), os.path.join(city_href, 'todas_especialidades')),
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs.copy()
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        2. Get specialities
        """

        print('Parse specialities page')

        specialities_options = response.css('#all-specialties-box #all-specialties-box-content a')

        city_name = kwargs['city_name']

        for option in specialities_options:
            spe_href = option.attrib['href']
            spe_name = option.css('::text').get().replace('\n', '').strip()
            kwargs['speciality_name'] = spe_name

            print('Parse specialities for city {}, speciality {}'.format(city_name, spe_name))

            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), spe_href),
                callback=self.__parse_services_page,
                cb_kwargs=kwargs.copy()
            )

    def __parse_services_page(self, response, **kwargs):
        """
        3. Get services
        """

        print('Parse services page for city {}'.format(kwargs['city_name']))

        services_options = response.css('.list-products .list-product')

        for option in services_options:
            option_href = option.css('.list-product-info a.mas_info_btn').attrib['href']

            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), option_href),
                callback=self.__parse_service,
                cb_kwargs=kwargs.copy()
            )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """
        print('Parse service start {}'.format(response.request.url))

        product_name = response.css('#product-box #product-box-info h1').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        pvp_full = response.css('#product-box #product-box-info #product-box-info-checkout #product-box-info-checkout-product-price .price').get()
        if pvp_full:
            pvp_full = pvp_full.lower().replace('\n', '').strip()
            pvp_full = BeautifulSoup(pvp_full, "lxml").text  # .replace(' ', '')
        else:
            pvp_full = ''

        pvp_consultation = response.css('#product-box #product-box-info #product-box-info-checkout #product-box-info-checkout-price').get()
        if pvp_consultation:
            pvp_consultation = pvp_consultation.lower().replace('\n', '').strip()
            pvp_consultation = BeautifulSoup(pvp_consultation, "lxml").text
        else:
            pvp_consultation = ''

        try:
            pvp = response.css('#product-box #product-box-info #product-box-info-checkout #product-box-info-checkout-reserva small').get().lower().replace('\n', '').strip()
            pvp = BeautifulSoup(pvp, "lxml").text.replace(' ', '')
            pvp = self.re_get_price(pvp)
        except:
            pvp = ''

        description = response.css('#product-box #product-tabs #tab-description')
        description = BeautifulSoup(description.get().replace('<br>', '\n'), "lxml").text.strip()

        speciality = kwargs['speciality_name']

        center_name = response.css('#product-box #product-box-info #clinic_link::text').get().replace('\n', '').strip()
        city = kwargs['city_name']

        address_list = []  # address.css('ul.dots') or []
        if len(address_list) == 0:
            address_list = response.css('#product-box #product-tabs #tab-clinic > p')
            if len(address_list) == 0:
                print('Error getting address %s' % response.request.url)
                return
            else:
                address_list = [address_list[1].css('::text').get()]
        else:
            address_list_tmp = []
            for ad in address_list:
                f = ''
                for st in ad.css('li strong'):
                    f += st.css('::text')
                if f != '':
                    address_list_tmp.append(f)
            if len(address_list_tmp) == 0:
                for ad in address_list:
                    f = ''
                    for st in ad.css('li'):
                        f += st.css('::text')
                    if f != '':
                        address_list_tmp.append(f)

            address_list = address_list_tmp
        address = '|'.join(address_list)

        try:
            obj, created = Record.objects.update_or_create(
                product_name=product_name,
                speciality_name=speciality,
                center=center_name,
                city=city,
                url=response.request.url,
                defaults={
                    'pvp': pvp,
                    'pvp_middle': pvp_consultation,
                    'pvp_full': pvp_full,
                    'description': description,
                    'address': address,
                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(response.request.url, e))

    def get_main_domain(self):
        return MAIN_DOMAIN
