# -*- coding: utf-8 -*-
import urllib.parse
import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import PortalsaludSanitasRecord as Record

MAIN_DOMAIN = 'https://portalsalud.sanitas.es/'
AJAX_MAP = {
    # url contains | center - provinces ajax post
    'chequeos-salud': 'https://portalsalud.sanitas.es/codigo/ajaxChequeoCentro.php',
    'chequeos-salud-modular': 'https://portalsalud.sanitas.es/codigo/ajaxChequeoModularCentro.php',
    'test-geneticos-preventivos': 'https://portalsalud.sanitas.es/codigo/ajaxTestCentro.php',
    'videoconsultas': 'https://portalsalud.sanitas.es/codigo/ajaxVideoconsultaPsicologia.php',
    'salud-deportiva': 'https://portalsalud.sanitas.es/codigo/ajaxDeporteCentro.php',
    'salud-casa': 'https://portalsalud.sanitas.es/codigo/ajaxCasaCentro.php',
    'salud-mujer': 'https://portalsalud.sanitas.es/codigo/ajaxMujerCentro.php'
}


class PortalsaludSanitasScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    1. Scrape main to get category list (https://portalsalud.sanitas.es)
    1.a. Get subcategory list (https://www.smartsalus.com/albacete)
    1.b. Get service https://www.smartsalus.com/albacete/vacunas/vacunas-bebes-y-ninos
    1.b.a. type 1 - Normal - https://portalsalud.sanitas.es/test-geneticos-preventivos/test-antigenos-covid19
    1.b.b. type 2 - Gender - https://portalsalud.sanitas.es/chequeos-salud/chequeo-complete
    1.b.c. type 3 - Online - https://portalsalud.sanitas.es/videoconsultas/psicologia-online
    1.b.d. type 4 - multi - https://portalsalud.sanitas.es/chequeos-salud/chequeo-modular
    1.b.e. type 5 - nothing - https://portalsalud.sanitas.es/chequeos-salud/chequeo-inteligente
    """

    name = 'portalsaludsanitas'
    start_urls = [
        MAIN_DOMAIN,
    ]

    def get_ajax_url(self, page_url: str):
        u = page_url.replace(MAIN_DOMAIN, '')
        if 'chequeo-modular' in u:
            return AJAX_MAP['chequeos-salud-modular']
        else:
            u = u.split('/')
            return AJAX_MAP[u[0]]

    def parse(self, response, **kwargs):
        """
        1. Get categories
        """
        print('PARSE START')

        categories_options = response.css('header .header nav a')

        for option in categories_options:
            cat_href = option.attrib['href']
            if cat_href in ['', '#', None]:
                continue

            cat_name = option.css('::text').get().replace('\n', '').strip()

            print('Parse category {}'.format(cat_name))

            kwargs['category_name'] = cat_name

            yield scrapy.Request(
                url=urllib.parse.urljoin(MAIN_DOMAIN, cat_href),
                callback=self.__parse_specialities_page,
                cb_kwargs=kwargs.copy()
            )

    def __parse_specialities_page(self, response, **kwargs):
        """
        1.a. Get sub-categories
        or
        1.b. Get service
        """

        print('Parse sub-categories page')

        subcategories_rows = response.css('main .c__box-slider')

        cat_name = kwargs['category_name']

        if len(subcategories_rows) > 0:
            for sub_cat_option in subcategories_rows:
                # Row name - Speciality
                # spe_name = sub_cat_option.css('.item-ppal .txt-item .title::text').get()
                # kwargs['speciality_name'] = spe_name
                # Get services boxes
                subcategories_options = sub_cat_option.css('.inner-pruebas a')
                for option in subcategories_options:
                    spe_href = option.attrib['href']
                    print('Parse specialities for category {}'.format(cat_name))
                    yield scrapy.Request(
                        url=urllib.parse.urljoin(MAIN_DOMAIN, spe_href),
                        callback=self.__parse_service,
                        cb_kwargs=kwargs.copy()
                    )
        else:
            # paths = response.request.url.replace(MAIN_DOMAIN, '').split('/')
            # kwargs['speciality_name'] = paths[0]
            yield scrapy.Request(
                url=response.request.url,
                callback=self.__parse_service,
                cb_kwargs=kwargs.copy(),
                dont_filter=True
            )

    def __parse_service(self, response, **kwargs):
        """
        4. Get service
        """
        print('Parse service start {}'.format(response.request.url))

        kwargs['url'] = response.request.url
        product_name = response.css('header h1').get().replace('\n', '')
        kwargs['product_name'] = BeautifulSoup(product_name, "lxml").text.strip()

        try:
            description_p_list = response.css('main .item-intro p')
            description = ''
            for description_p in description_p_list:
                description += BeautifulSoup(
                    description_p.get().replace('<br>', '\n').replace('<p>', '\n').replace('<li>', '\n'),
                    "lxml").text.strip()
            description = self.re_replace_multi_jump_line(description)
            if len(description) > 1200:
                description = description[:1200] + '...'
        except Exception as e:
            print(e)
            description = ''
        kwargs['description'] = description

        try:
            includes = ''
            body_nav = response.css('.tabs-ficha ul.tabs a')
            for nav in body_nav:
                nav_href = nav.attrib['href']
                nav_name = nav.css('::text').get().replace('\n', '').lower().strip()

                if 'qué incluye' in nav_name:
                    a = '.tabs-ficha .tabgroup.ficha #{}'.format(nav_href.replace('#', ''))
                    includes = response.css(a).get().replace('<br>', '\n').replace('<li>', '\n').replace('<p>', '\n')
                    b = BeautifulSoup(includes, "lxml").text
                    includes = self.re_replace_multi_jump_line(b).strip()
        except Exception as e:
            print(e)
            includes = ''
        kwargs['includes'] = includes

        breadcrumbs = response.css('.breadcrumbs a')
        kwargs['speciality_name'] = breadcrumbs[1].css('::text').get()

        #
        # Check kind of template

        if response.css('.form-interna select#sexo'):
            # Has gender selector
            # Example: https://portalsalud.sanitas.es/chequeos-salud/chequeo-complete
            print('Gender type template')

            try:
                pvp_full = self.re_get_price(response.css('.c__intro-form .item-precio span::text').get())
            except:
                pvp_full = ''
            kwargs['pvp_full'] = pvp_full
            kwargs['pvp'] = ''

            form_id = response.xpath('//form[@id="form_datos"]//input[@name="id"]/@value').get()
            kwargs['ajax_center_url'] = self.get_ajax_url(response.request.url)
            for option in ['mujer', 'hombre']:
                kwargs['gender'] = option
                yield scrapy.Request(
                    url=self.get_complete_url_with_params(
                        self.get_ajax_url(response.request.url), dict(id=str(form_id), sexo=option, id_provincia="0")
                    ),
                    callback=self.__parse_gender_provinces,
                    method='POST',
                    cb_kwargs=kwargs.copy()
                )

        elif response.css('.form-interna select#plan'):
            # Example: https://portalsalud.sanitas.es/videoconsultas/psicologia-online
            print('Online type template')
            # Is online plan
            kwargs['province_name'] = 'ONLINE'
            kwargs['center_name'] = 'ONLINE'
            kwargs['address'] = 'ONLINE'
            kwargs['pvp'] = ''
            prices_list = []
            for p in response.css('.form-interna select#plan option'):
                value = p.attrib['value']
                if value == '':
                    continue
                name = BeautifulSoup(p.get(), "lxml").text.replace('\n', '').strip()
                name = name.split('-')
                n = int(self.re_get_price(name[0]))
                pvp = int(self.re_get_price(name[1]))
                pvp = str(n * pvp)
                prices_list.append('%s=%s' % ('-'.join(name), pvp))
            kwargs['pvp_full'] = '|'.join(prices_list)

            self.save_service(kwargs)

        elif response.css('.form-interna > .item-select > .item-selection'):
            # Example: https://portalsalud.sanitas.es/chequeos-salud/chequeo-modular
            print('Province type template')
            # Multi : checkbox
            kwargs['pvp'] = ''
            kwargs['pvp_full'] = ''
            products_list = response.css('.form-interna .item-select .inner-body .item label')
            products_list_array = []
            for p in products_list:
                arr = p.css('span::text').get().split('(')
                name = arr[0].strip()
                price = self.re_get_price(arr[1])
                products_list_array.append('%s:%s' % (name, price))
            kwargs['includes'] += 'SERVICIOS_MODULARES=' + '|'.join(products_list_array)

            form_id = response.xpath('//form[@class="form-interna"]//input[@name="id"]/@value').get()

            for p in response.css('.form-interna select#id_provincia option'):
                value = p.attrib['value']
                name = p.css('::text').get()
                kwargs['province_name'] = name

                yield scrapy.Request(
                    url=self.get_complete_url_with_params(
                        self.get_ajax_url(response.request.url), dict(id=str(form_id), id_provincia=str(value))
                    ),
                    callback=self.__parse_centers,
                    method='POST',
                    cb_kwargs=kwargs.copy()
                )

        elif response.css('.form-interna #id_provincia'):
            print('Province type template')
            # Normal : province + centers
            form_id = response.xpath('//form[@id="form_datos"]//input[@name="id"]/@value').get()
            try:
                pvp_full = self.re_get_price(response.css('.c__intro-form .item-precio span::text').get())
            except:
                pvp_full = ''
            kwargs['pvp_full'] = pvp_full
            kwargs['pvp'] = ''

            for p in response.css('.form-interna select#id_provincia option'):
                value = p.attrib['value']
                if value == '':
                    continue
                name = p.css('::text').get()
                kwargs['province_name'] = name

                yield scrapy.Request(
                    url=self.get_complete_url_with_params(
                        self.get_ajax_url(response.request.url), dict(id=str(form_id), id_provincia=str(value))
                    ),
                    callback=self.__parse_centers,
                    method='POST',
                    cb_kwargs=kwargs.copy()
                )

        else:
            print('None type template')
            kwargs['province_name'] = response.css('.c__intro-form .box-inteligente::text').get()
            kwargs['center_name'] = ''
            kwargs['address'] = ''
            kwargs['pvp'] = ''
            kwargs['pvp_full'] = ''
            self.save_service(kwargs)

    def __parse_gender_provinces(self, response, **kwargs):
        options = response.css('option')
        for option in options:
            value = option.attrib['value']
            name = option.css('::text').get()
            if value == '':
                continue
            kwargs['province_name'] = name
            yield scrapy.Request(
                url=self.get_complete_url_with_params(kwargs['ajax_center_url'], dict(id="1", sexo=kwargs['gender'], id_provincia=str(value))),
                callback=self.__parse_centers,
                method='POST',
                cb_kwargs=kwargs.copy(),
            )

    def __parse_centers(self, response, **kwargs):
        centers = response.css('a')

        centers_list = []
        address_list = []

        for center in centers:
            p = center.css('p')
            center_name = p[0].css('strong::text').get()
            address = p[1].css('::text').get()
            centers_list.append(center_name)
            address_list.append(address)
        kwargs['center_name'] = '|'.join(centers_list)
        kwargs['address'] = '|'.join(address_list)

        self.save_service(kwargs)

    def __parse_plans(self, response, **kwargs):
        centers = response.css('a')

        centers_list = []
        address_list = []

        for center in centers:
            p = center.css('p')
            center_name = p[0].css('strong::text').get()
            address = p[1].css('::text').get()
            centers_list.append(center_name)
            address_list.append(address)
        kwargs['center_name'] = '|'.join(centers_list)
        kwargs['address'] = '|'.join(address_list)

        self.save_service(kwargs)

    def save_service(self, kwargs):
        g = kwargs.get('gender', None)
        if g:
            g = Record.GENDER_MALE if g == 'hombre' else Record.GENDER_FEMALE
        try:
            obj, created = Record.objects.update_or_create(
                product_name=kwargs['product_name'],
                speciality_name=kwargs['speciality_name'],
                center=kwargs['center_name'],
                province_name=kwargs['province_name'],
                gender=g,
                url=kwargs['url'],
                defaults={
                    'pvp': kwargs.get('pvp', ''),
                    'pvp_full': kwargs['pvp_full'],
                    'description': kwargs['description'],
                    'includes': kwargs['includes'],
                    'excludes': '',
                    'address': kwargs['address'],
                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(kwargs['url'], e))
