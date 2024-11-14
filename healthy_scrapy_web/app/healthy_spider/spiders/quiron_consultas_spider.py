# -*- coding: utf-8 -*-
import json

import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import QuironRecord as Record


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

    name = 'quiron_consultas'
    start_urls = [
        'https://e-quironsalud.es/'
    ]

    def parse(self, response, **kwargs):
        print('START PARSE')
        selector = response.css('div#product-infos-tabs-content #especialidad-tc')
        selector_options = selector.css('option')

        for option in selector_options:
            value = option.attrib['value']
            if value in ['', None, '[]', 'None', 'null']:
                continue
            attr_id = option.attrib['attributeid']
            name = option.css('::text').get()

            print('Parse option {}'.format(name))

            yield scrapy.FormRequest(
                url=self.__get_provinces_url(value, attr_id),
                callback=self.__parse_provinces,
                method='POST',
                cb_kwargs=dict(speciality_value_id=value, speciality_attr_id=attr_id, speciality_name=name),
            )

    def __parse_provinces(self, response, **kwargs):
        """
        :param request:
        :return:
        """
        print('Parse provinces start {}'.format(response.request.url))
        speciality_value_id = kwargs['speciality_value_id']
        speciality_attr_id = kwargs['speciality_attr_id']
        rs_json = json.loads(response.body)
        for province in rs_json:
            # id_state = province['id_state']
            province_name = province['name']
            kwargs['province_name'] = province_name
            print('Parse provinces province {}'.format(province_name))
            yield scrapy.Request(
                url=self.__get_product_url(speciality_value_id, speciality_attr_id, province_name),
                callback=self.__parse_product,
                cb_kwargs=kwargs
            )

    def __parse_product(self, response, **kwargs):
        """
        :param response:
        :return:
        """
        print('Parse product start {}'.format(response.request.url))
        # Get details for product of kind at the moment
        type_product_name = 'Presencial' if ('is_physic' in kwargs and kwargs['is_physic'] is True) else 'Telefónico'

        product_name = response.css('div.product_header_container h1.page-title').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        description = response.css('div#description div.product-description .rte-content').get()
        description = BeautifulSoup(description, "lxml").text.strip()

        group_5 = response.css('input#radio-attribute-consulta')[1].xpath('@value').get()
        # product_id = response.css('#product_page_product_id').xpath('@value').get()
        product_attr = response.css('#idProductAttribute').xpath('@value').get()
        token = response.css('form#add-to-cart-or-refresh input[name="token"]').xpath('@value').get()
        speciality = kwargs['speciality_name']
        pvp = response.css('div.product-prices span.product-price::text').get().replace('€', '').replace(' ', '')

        selector_provinces_options = response.css('#provincias_cita option')

        id_product_attr = response.css('#add-to-cart-or-refresh #idProductAttribute').xpath('@value').get()
        product_id = response.css('#add-to-cart-or-refresh #product_page_product_id').xpath('@value').get()

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

            yield scrapy.Request(
                url=self.__get_centers_from_province_url(value, product_id, id_product_attr),
                callback=self.__parse_centers_for_province,
                cb_kwargs=kwargs
            )

        # if not 'is_physic' in kwargs or ('is_physic' in kwargs and kwargs['is_physic'] is False):
        # kwargs['is_physic'] = True
        yield scrapy.FormRequest(
            url=self.__get_product_action_kind_url(token, product_id, group_5, [product_id, product_attr]),
            callback=self.__parse_product_physic,
            method='POST',
            cb_kwargs=kwargs,
        )

    def __parse_product_physic(self, response, **kwargs):
        """
        :param response:
        :return:
        """
        print('Parse product physic start {}'.format(response.request.url))

        # Check is physic page
        is_physic_option = 'checked' in response.css('ul#group_5 li').getall()[1]

        if not is_physic_option:
            yield None

        # Get details for product of kind at the moment
        type_product_name = 'Presencial'

        product_name = response.css('div.product_header_container h1.page-title span').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        description = response.css('div#description div.product-description .rte-content').get()
        description = BeautifulSoup(description, "lxml").text.strip()

        speciality = kwargs['speciality_name']
        pvp = response.css('div.product-prices span.product-price::text').get().replace('€', '').replace(' ', '')

        selector_provinces_options = response.css('#provincias_cita option')

        id_product_attr = response.css('#add-to-cart-or-refresh #idProductAttribute').xpath('@value').get()
        product_id = response.css('#add-to-cart-or-refresh #product_page_product_id').xpath('@value').get()

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

            yield scrapy.Request(
                url=self.__get_centers_from_province_url(value, product_id, id_product_attr),
                callback=self.__parse_centers_for_province,
                cb_kwargs=kwargs
            )

    def __parse_centers_for_province(self, response, **kwargs):
        """
        From json response, get all centers to a list.
        :param response:
        :param kwargs:
        :return:
        """
        print('Parse centers for province {}'.format(response.request.url))

        rs_json = json.loads(response.body)
        type_product_name = kwargs['type_product_name']
        product_name = kwargs['product_name']
        speciality = kwargs['speciality']
        pvp = kwargs['pvp']
        pvp = pvp[:64] if pvp is not None else ''
        province_name = kwargs['province_name']
        url = kwargs['url']
        description = kwargs['description']

        # Go over centers
        for center in rs_json:
            center_name = center['name']
            try:
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

    def __get_provinces_url(self, speciality_value_id, speciality_attr_id):
        return 'https://e-quironsalud.es/?module=citacion&fc=module&controller=datos&action=GetProvinciasBuscador&productId={}&idProductAttribute={}'.format(
            speciality_value_id,
            speciality_attr_id
        )

    def __get_product_url(self, speciality_value_id, speciality_attr_id, province_name=''):
        return 'https://e-quironsalud.es/index.php?id_product={}&id_product_attribute={}&controller=product'.format(
            speciality_value_id,
            speciality_attr_id,
        )

    def __get_product_action_kind_url(self, token, id_product, group_id, product_id_list):
        return 'https://e-quironsalud.es/index.php?controller=product?token={}&id_product={}&id_customization=0&group[5]={}{}'.format(
            token,
            id_product,
            group_id,
            '&productId=' + ','.join(product_id_list)
        )

    def __get_centers_from_province_url(self, province_id, product_id, id_product_attr):
        return 'https://e-quironsalud.es/index.php?module=citacion&fc=module&controller=datos&action=CitaProvincia&provinciaId={}&productId={}&idProductAttribute={}'.format(
            province_id,
            product_id,
            id_product_attr
        )

