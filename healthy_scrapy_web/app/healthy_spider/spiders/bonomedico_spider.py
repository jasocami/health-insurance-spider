# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import BonomedicoRecord as Record

MAIN_DOMAIN = 'https://www.bonomedico.es/'


class BonomedicoScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get all provinces list https://www.bonomedico.es/
    2. Get specialities list https://www.bonomedico.es/madrid
    3. Get services list
    3.1 type a unique item : https://www.bonomedico.es/madrid/cirugia-plastica/mamoplastia
    3.2 type b multi item : https://www.bonomedico.es/las-palmas/cirugia-plastica/mamoplastia
    4. Get service
    4.1 type a no price : https://www.bonomedico.es/valencia/tratamientos-pelo/injerto-capilar/microinjerto-capilar-en-valencia
    4.2 type b multi price : https://www.bonomedico.es/madrid/cirugia-plastica/liposuccion/liposuccion-madrid
    4.3 type c unique price : https://www.bonomedico.es/madrid/cirugia-plastica/blefaroplastia/clinica-coro-blefaroplastia
    """

    name = 'bonomedico'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        """
        1. Get provinces
        """
        print('PARSE START')

        options = response.css('#menu-provincias-modal nav li a')

        for option in options:
            href = option.attrib['href']
            name = option.css('::text').get().replace('\n', '').strip()
            print('Parse province {}'.format(name))
            kwargs['pro_name'] = name
            yield scrapy.Request(
                url=href,
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        2. Get specialities list
        """

        print('Parse specialities page')

        options = response.css('#todo-listado .listado-raiz-categoria')

        pro_name = kwargs['pro_name']

        for option in options:
            for link in option.css('ul a'):
                href = link.attrib['href']
                name = link.css('::text').get().replace('\n', '').strip()
                kwargs['speciality_name'] = name
                print('Parse province {}, speciality {}'.format(pro_name, name))
                yield scrapy.Request(
                    url=href,
                    callback=self.__parse_services_list,
                    cb_kwargs=kwargs
                )

    def __parse_services_list(self, response, **kwargs):
        """
        3. Get services list
        """

        print('Parse services list start {}'.format(response.request.url))

        items = response.css('#todo-listado > .subcategoria > .subsubcategorias-listado > .subsubcategoria')
        for item in items:
            for row in item.css('.productos-listado .producto'):
                href = row.css('.precios-boton a').attrib['href']
                yield scrapy.Request(
                    url=href,
                    callback=self.__parse_service,
                    cb_kwargs=kwargs
                )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """

        print('Parse service start {}'.format(response.request.url))

        pvp, pvp_full = '', ''
        product_name = response.css('.modulo-sidebar .product-prices')
        if product_name:
            # There is a list of prices
            name_list = []
            prices_list = []
            for items in product_name.css('tr'):
                items = items.css('td')
                name = BeautifulSoup(items[0].get().replace('\n', '').replace('\t', ''), "lxml").text.strip()
                price = BeautifulSoup(items[1].get().replace('\n', '').replace('\t', '').replace('€', '').strip(), "lxml").text.strip()
                if price:
                    try:
                        price = self.re_get_price(price)
                    except:
                        price = ''
                name_list.append(name)
                prices_list.append(price)
            pvp_full = '|'.join(prices_list)
            product_name = '|'.join(name_list)

        if not product_name:
            product_name = response.css('.cabecera-inner .cabecera-inner-inner h1').get()
            if product_name:
                product_name = BeautifulSoup(product_name, "lxml").text.strip()

        if not product_name:
            product_name = response.css('.main-title h1').get()
            if product_name:
                product_name = BeautifulSoup(product_name, "lxml").text.strip()

        if not pvp_full:
            try:
                pvp_full = response.css('head title').get()
                pvp_full = pvp_full.lower().replace('\n', '').strip()
                pvp_full = BeautifulSoup(pvp_full, "lxml").text
                pvp_full = self.re_get_price(pvp_full)
            except:
                pvp_full = ''

        description = response.css('#cuerpo-producto #descripcion-producto').get()
        description = BeautifulSoup(description.replace('<br>', '\n'), "lxml").text.strip()
        description = self.re_replace_multi_jump_line(description)[:1200] + '...'

        speciality = kwargs['speciality_name']

        center_name = response.css('#donde > .donde')
        if center_name:
            address_list = []
            centers_list = []
            for row in center_name:
                rol = row.css('.donde-rol::text').get().replace('\n', '').strip()
                for center in row.css('.listado-centros-donde li'):
                    c_name = '{}:{}'.format(rol, center.css('a::text').get())
                    ad = center.css('.donde-centro::text').get().replace('\n', '').strip()
                    centers_list.append(c_name)
                    address_list.append(ad)
            address = '|'.join(address_list)
            center_name = '|'.join(centers_list)
        else:
            center_name = ''
            address = ''

        includes = response.css('#listados-incluidos #servicios-incluidos li')
        if includes:
            includes_final = []
            for include in includes:
                a = include.css('::text').get()
                a = BeautifulSoup(a.replace('<br>', '\n').replace('<li>', '\n'), "lxml").text
                includes_final.append(self.re_replace_multi_jump_line(a).strip())
            includes = '|'.join(includes_final)
        else:
            includes = ''

        excludes = response.css('#listados-incluidos #servicios-no-incluidos li')
        if excludes:
            excludes_final = []
            for exclude in excludes:
                a = exclude.css('::text').get()
                a = BeautifulSoup(a.replace('<br>', '\n').replace('<li>', '\n'), "lxml").text
                excludes_final.append(self.re_replace_multi_jump_line(a).strip())
            excludes = '|'.join(excludes_final)
        else:
            excludes = ''

        try:
            obj, created = Record.objects.update_or_create(
                product_name=product_name,
                speciality_name=speciality,
                center=center_name,
                province_name=kwargs['pro_name'],
                url=response.request.url,
                defaults={
                    'pvp': pvp,
                    'pvp_full': pvp_full,
                    'includes': includes,
                    'excludes': excludes,
                    'description': description,
                    'address': address,
                    'health_registration': '',
                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(response.request.url, e))

    def get_main_domain(self):
        return MAIN_DOMAIN
