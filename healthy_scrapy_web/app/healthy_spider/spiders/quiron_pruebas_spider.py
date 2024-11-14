# -*- coding: utf-8 -*-
import json
import urllib.parse

import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import QuironRecord as Record

MAIN_DOMAIN = 'https://e-quironsalud.es/'


class QuironScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.
    1. Scrap home to get all specialities (html)
    2. Call api for each speciality to get provinces for it with these dynamic params: (json)
        - productId > speciality_value_id
        - idProductAttribute > speciality_attr_id
    3. Each product has two kind: phone and physic.
        3.1 Call api to get product for that province with these dynamic params: by default is phone contact (html)
            - id_product > speciality_value_id
            - id_product_attribute > speciality_attr_id
            - provincia > province_name
        3.2 Call api to get product for physic contact with these dynamic params: (html)
            - token > in form #add-to-cart-or-refresh > token input
            - id_product > input#product_page_product_id
            - productId > array: #product_page_product_id,#idProductAttribute
            - group[5] > value from input#radio-attribute-consulta
        3.x.1 Call api to get centers for province in product. With these dynamic params: (json)
            - idProductAttribute > #idProductAttribute
            - productId > #product_page_product_id
            - provinciaId > province id from selector
    """

    name = 'quiron_pruebas'
    start_urls = [
        MAIN_DOMAIN
    ]

    def parse(self, response, **kwargs):
        print('PARSE START')

        by_image_items = response.css('nav#cbp-hrmenu div.menu-element-id-29 div.menu_row div.cbp-menu-column-inner div.col-12')
        tests_items = response.css('nav#cbp-hrmenu div.menu-element-id-39 div.menu_row div.cbp-menu-column-inner div.col-12')
        aesthetic_items = response.css('nav#cbp-hrmenu div.menu-element-id-9 div.cbp-products-list div.col-12')
        eye_items = response.css('nav#cbp-hrmenu div.menu-element-id-1 div.cbp-products-list div.col-12')

        all_items = by_image_items + tests_items + aesthetic_items + eye_items

        for item in all_items:
            href = item.css('a.cbp-product-name').attrib['href']
            name = item.css('a.cbp-product-name::text').get().replace('\n', '').strip()
            print('Parsing {}'.format(name))

            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), href),
                callback=self.__parse_product,
            )

    def __parse_product(self, response, **kwargs):
        """
        :param response:
        :return:
        """
        print('Parse product start {}'.format(response.request.url))

        # Get details for product of kind at the moment
        type_product_name = '(vacío)'

        product_name = response.css('div.product_header_container h1.page-title').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        description = response.css('div#description div.product-description .rte-content').get()
        description = BeautifulSoup(description, "lxml").text.strip()

        product_id = response.css('#product_page_product_id').xpath('@value').get()
        speciality = ''  # kwargs['speciality_name']
        pvp = response.css('div.product-prices span.product-price::text').get().replace('€', '').replace(' ', '').strip()
        selector_provinces_options = response.css('#provincias_cita_otros option')

        if len(selector_provinces_options) > 0:
            # List options provinces to get centers
            for option in selector_provinces_options:
                value = option.xpath('@value').get()
                if value in ['', None, 'todas', 'Todas', 'todos', 'Todos']:
                    continue
                province_name = option.css('::text').get()

                kwargs['type_product_name'] = type_product_name
                kwargs['product_name'] = product_name
                kwargs['speciality'] = speciality
                kwargs['pvp'] = pvp
                kwargs['province_name'] = province_name
                kwargs['url'] = response.request.url
                kwargs['description'] = description

                yield scrapy.FormRequest(
                    url=self.__get_centers_from_province_url(response.request.url, value, product_id),
                    callback=self.__parse_centers_for_province,
                    method='POST',
                    cb_kwargs=kwargs
                )
        else:
            kwargs['type_product_name'] = type_product_name
            kwargs['product_name'] = product_name
            kwargs['speciality'] = speciality
            kwargs['pvp'] = pvp
            kwargs['province_name'] = ''
            kwargs['url'] = response.request.url
            kwargs['description'] = description
            kwargs['center_name'] = ''

            self.save_record(**kwargs)

    def __parse_centers_for_province(self, response, **kwargs):
        """
        From json response, get all centers to a list.
        :param response:
        :param kwargs:
        :return:
        """
        print('Parse centers for province start {}'.format(response.request.url))
        rs_json = json.loads(response.body)

        # Go over centers
        for center in rs_json:
            kwargs['center_name'] = center['name']
            self.save_record(**kwargs)

    def save_record(self, **kwargs):
        try:
            type_product_name = kwargs['type_product_name']
            product_name = kwargs['product_name']
            speciality = kwargs['speciality']
            pvp = kwargs['pvp']
            pvp = pvp[:64] if pvp is not None else ''
            province_name = kwargs['province_name']
            center_name = kwargs['center_name']
            url = kwargs['url']
            description = kwargs['description']
            obj, created = Record.objects.update_or_create(
                    type_product_name=type_product_name,
                    product_name=product_name,
                    speciality_name=speciality,
                    center=center_name,
                    province_name=province_name,
                    url=url,
                    defaults={
                        'pvp': pvp,
                        'description': description,
                        'group': 'Consulta'
                    }
                )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(kwargs['url'], e))


    def __get_centers_from_province_url(self, url, province_id, product_id):
        return '{}?module=citacion&fc=module&controller=datos&action=CitaProvinciaOtros&provinciaId={}&productId={}'.format(
            url,
            province_id,
            product_id
        )

    def get_main_domain(self):
        return MAIN_DOMAIN
