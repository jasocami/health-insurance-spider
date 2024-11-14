# -*- coding: utf-8 -*-
import re

import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import SmartSalusRecord as Record

MAIN_DOMAIN = 'https://www.smartsalus.com/'


class SmartSalusScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get all provinces list (https://www.smartsalus.com/)
    2. Get specialities list (https://www.smartsalus.com/albacete)
    3. Get services https://www.smartsalus.com/albacete/vacunas/vacunas-bebes-y-ninos
    4. Get service (https://www.smartsalus.com/albacete/vacunas-en-albacete-3511)
    """

    name = 'smartsalus'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        """
        1. Get provinces
        """
        print('PARSE START')

        provinces_options = response.css('div.footer-cities a')

        for option in provinces_options:
            pro_href = option.attrib['href']
            pro_name = option.css('::text').get().replace('\n', '').strip()

            print('Parse province {}'.format(pro_name))

            kwargs['pro_name'] = pro_name

            yield scrapy.Request(
                url=pro_href,
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        2. Get specialities
        """

        print('Parse specialities page')

        specialities_options = response.css('.page.ciudad .container nav a')

        pro_name = kwargs['pro_name']

        for option in specialities_options:
            spe_href = option.attrib['href']
            spe_name = option.css('::text').get().replace('\n', '').strip()
            # kwargs['speciality_name'] = spe_name

            print('Parse specialities for province {}, speciality {}'.format(pro_name, spe_name))

            yield scrapy.Request(
                url=spe_href,
                callback=self.__parse_services_page,
                cb_kwargs=kwargs
            )

    def __parse_services_page(self, response, **kwargs):
        """
        3. Get services
        """

        print('Parse services page')

        specialities_options = response.css('.page.especialidad article .details h2 a')

        pro_name = kwargs['pro_name']

        for option in specialities_options:
            ser_href = option.attrib['href']
            ser_name = option.css('::text').get().replace('\n', '').strip()

            print('Parse services for province {}, speciality {}'.format(pro_name, ser_name))

            yield scrapy.Request(
                url=ser_href,
                callback=self.__parse_service,
                cb_kwargs=kwargs
            )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """
        print('Parse service start {}'.format(response.request.url))

        # Get details for product of kind at the moment
        product_name = response.css('article.plan h1.title-3rd').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        speciality_items = response.css('#main .breadcrumb a')
        speciality = []
        for item in speciality_items:
            it = item.get().replace('\n', '').strip()
            it = BeautifulSoup(it, "lxml").text.strip()
            speciality.append(it)
        speciality = speciality[2]

        pvp = response.css('article.plan .btn-reservar').get().lower().replace('\n', '').strip()
        pvp = BeautifulSoup(pvp, "lxml").text.replace(' ', '')
        try:
            pvp = self.re_get_price(pvp)
        except:
            pvp = ''

        pvp_full = response.css('article.plan .price .price-smart').get().lower().replace('\n', '').strip()
        pvp_full = BeautifulSoup(pvp_full, "lxml").text.replace(' ', '')
        try:
            pvp_full = self.re_get_price(pvp_full)
        except:
            pvp_full = ''

        boxes = response.css('div.plan-info div#desc > div.box')
        try:
            description = boxes[0]
            description = BeautifulSoup(
                description.get().replace('<br>', '\n'),
                "lxml").text.strip()
        except Exception as e:
            print('Exception: Description is empty {}. Except: '.format(response.request.url, e))
            description = ''

        try:
            includes = boxes[1]
            includes = self.re_replace_multi_jump_line(
                BeautifulSoup(includes.get().replace('<br>', '\n').replace('<li>', '\n'),"lxml").text.strip()
            )
        except Exception as e:
            print(e)
            includes = ''

        excludes = ''

        center_name = response.css('article.plan  .proveidor-plan::text').get().replace('\n', '').strip()
        province = kwargs['pro_name']
        address = response.css('#centro-medico div div div > span')
        address = ', '.join([ex.css('::text').get() for ex in address])

        try:
            latitude = response.css('input#latitud').attrib['value'][:30]
            longitude = response.css('input#longitud').attrib['value'][:30]
        except:
            latitude = ''
            longitude = ''

        try:
            health_registration = response.css('#centro-medico div div div > strong::text').get().replace('\n', '').strip()
        except:
            health_registration = ''
        city = ''  #
        town = ''  # Not found in web

        # List options provinces to get centers
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
                    'pvp': pvp,
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
