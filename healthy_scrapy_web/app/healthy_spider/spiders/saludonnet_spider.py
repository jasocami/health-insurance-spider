# -*- coding: utf-8 -*-
import json
import urllib.parse

import scrapy
from bs4 import BeautifulSoup

from healthy_spider.spiders.base_spider import BaseScrape
from healthy_spider_records.models import SaludonnetRecord as Record

MAIN_DOMAIN = 'https://www.saludonnet.com/'
PROVINCES_URL = 'https://www.saludonnet.com/api/v0/provinces'


class SaludOnNetScrape(BaseScrape):
    """
    On this spider, we need to do few steps to receive all the info we want.

    """

    name = 'saludonnet'
    start_urls = [
        PROVINCES_URL
    ]

    def parse(self, response, **kwargs):
        print('PARSE START')

        rs_json = json.loads(response.body)

        dict = {
            'provinces_list': rs_json
        }

        yield scrapy.Request(
            url=self.get_main_domain(),
            callback=self.__parse_main_page,
            cb_kwargs=dict
        )

    def __parse_main_page(self, response, **kwargs):
        """
        :param request:
        :return:
        """

        print('Parse main page')

        specialities_options = response.css('div#specialtiesContainer div#listOfSpecialties a.linkOfSpecialty')

        for option in specialities_options:
            spe_href = option.attrib['href']
            spe_name = option.css('::text').get()
            spe_href_name = spe_href.split('/')[-1]

            for province in kwargs['provinces_list']:
                p_id = province['id']
                p_name = province['name']

                # Get all services for individual speciality and province
                print('Parse services for province {}, speciality {}'.format(p_name, spe_name))
                kwargs['province_id'] = p_id
                kwargs['province_name'] = p_name
                kwargs['speciality_name'] = spe_name
                kwargs['speciality_href_name'] = spe_href_name
                yield scrapy.Request(
                    url=self.__get_services_url(spe_href_name, p_id),
                    callback=self.__parse_services,
                    cb_kwargs=kwargs
                )

    def __parse_services(self, response, **kwargs):
        """
        :param response:
        :return:
        """
        print('Parse services API start {}'.format(response.request.url))

        # Get details for product of kind at the moment
        cards = response.css('div.procedures__results div#categoriesContainer .card')
        # Parse centers
        # https://www.saludonnet.com/sin-seguro-medico/api/v0/find/services?healthService=4222-servicio-de-podologia-quirop&specialty=podologia&province=madrid&city=&isSearchingByStreet=False&lat=0&lon=0&radiusInKm=0&userLatitude=40.4166&userLongitude=-3.7003&resultsPerPage=30&keyword=&orderBy=price&page=0
        # healthService = last href path of this services box call
        # specialty = speciality href name
        # province = province href mane
        # page = nº page to search starts with 0

        for card in cards:
            href = card.css('div.description-wrapper .button-medium.md-trigger.btn').attrib['href'].split('/')[-1]
            if '?' in href:
                href = href.split('?')[0]
            yield scrapy.Request(
                    url=self.__get_centers_api(href, kwargs['speciality_href_name'], kwargs['province_id'], 0),
                    callback=self.__parse_centers_by_api,
                    cb_kwargs=kwargs
                )

    def __parse_centers_by_api(self, response, **kwargs):
        """
        Parse services list by api json response
        """
        rs_json = json.loads(response.body)
        products = rs_json['products']
        total = rs_json['totalProducts']

        for product in products:
            href = product['url']

            pvp_full = product['price']
            has_pvp = product['hasInformativeConsultation']
            pvp = ''
            if has_pvp:
                pvp = product.get('relatedInformativeConsultationPrice', '')

            kwargs['pvp'] = pvp
            kwargs['pvp_full'] = pvp_full
            yield scrapy.Request(
                url=urllib.parse.urljoin(self.get_main_domain(), href),
                callback=self.__parse_service,
                cb_kwargs=kwargs
            )

        if total > 29 and len(products) > 0:
            params = self.__get_url_params(response.request.url)
            yield scrapy.Request(
                url=self.__get_centers_api(
                    params['healthService'][0], params['specialty'][0], params['province'][0], int(params['page'][0])+1
                ),
                callback=self.__parse_centers_by_api,
                cb_kwargs=kwargs
            )

    def __parse_service(self, response, **kwargs):
        """
        :param response:
        :return:
        """
        print('Parse service start {}'.format(response.request.url))

        # Get details for product of kind at the moment
        product_name = response.css('div.product__header__filter h1.main-title').get().replace('\n', '')
        product_name = BeautifulSoup(product_name, "lxml").text.strip()

        speciality = kwargs['speciality_name']

        pvp = kwargs.get("pvp")
        if pvp is None:
            pvp = (response.css('span#InformativeAppointmentPrice::text').get() or '').replace('€', '').strip()[:64]
        else:
            if type(pvp) == str:
                pvp = pvp.replace('€', '').strip()[:64]
            # else if is int do nothing

        pvp_full = ((str(kwargs.get("pvp_full")) or response.css('span#productPriceDesktop::text').get()) or '').replace('€', '').strip()[:64]
        group = 'Consulta'
        description = response.css('div.l-content-wrapper div.content-wrapper .tabs-wrapper #tab-container #tabGeneral .list')[0].get()
        description = BeautifulSoup(description, "lxml").text.strip()
        center_name = response.css('div.product__header__filter a#productProviderName::text').get()
        address = response.css('div.product__header__filter .product-header__address::text').get()
        province = response.css('.breadcrumb__links a#breadCrumbProvince span::text').get()  # kwargs['province_name']

        try:
            latitude = response.css('label#providerLatitude::text').get()
            longitude = response.css('label#providerLongitude::text').get()
        except:
            latitude = ''
            longitude = ''

        try:
            health_registration = response.css('div.product__header__filter .product-header__health-registration::text').get().split(':')[-1].strip()
        except:
            health_registration = ''
        city = response.css('.breadcrumb__links a#breadCrumbCity span::text').get()
        town = ''  # Not found in web
        try:
            includes_list = response.css('div.l-content-wrapper > div.content-wrapper .tabs-wrapper #tab-container #tabGeneral .list')[1].css('li')
            includes = '|'.join([ex.css('::text').get() for ex in includes_list])
        except:
            includes = ''
        try:
            excludes_list = response.css('div.l-content-wrapper > div.content-wrapper .tabs-wrapper #tab-container #tabGeneral .list')[2].css('li')
            excludes = '|'.join([ex.css('::text').get() for ex in excludes_list])
        except:
            excludes = ''

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
                    'group': group,
                    'health_registration': health_registration,
                    'latitude': latitude,
                    'longitude': longitude,

                }
            )
            print('Object {} | is new {}'.format(obj, created))
        except Exception as e:
            print('Error for url {} || {}'.format(response.request.url, e))

    def __get_services_url(self, speciality_name, province_id):
        return 'https://www.saludonnet.com/servicios-medicos/{}/provincia/{}'.format(
            speciality_name,
            province_id,
        )

    def __get_centers_api(self, health_service, speciality, province, page):
        return "https://www.saludonnet.com/sin-seguro-medico/api/v0/find/services" \
               "?healthService={}" \
               "&specialty={}" \
               "&province={}" \
               "&city=&isSearchingByStreet=False&lat=0&lon=0&radiusInKm=0" \
               "&userLatitude=0.4166&userLongitude=-0.7003&resultsPerPage=30&keyword=&orderBy=price&page={}".format(
                health_service, speciality, province, page
        )

    def __get_url_params(self, url):
        parsed = urllib.parse.urlparse(url)
        return urllib.parse.parse_qs(parsed.query)

    def get_main_domain(self):
        return MAIN_DOMAIN

    # https://www.saludonnet.com/servicios-medicos/oftalmologia/ciudad/sevilla-utrera
    # api https://www.saludonnet.com/sin-seguro-medico/api/v0/find/services?healthService=pack-38-consulta-de-oftalmologia--campimetria&specialty=oftalmologia&province=sevilla&city=&isSearchingByStreet=False&lat=0&lon=0&radiusInKm=0&userLatitude=0.4166&userLongitude=-0.7003&resultsPerPage=30&keyword=&orderBy=price&page=
    # api https://www.saludonnet.com/sin-seguro-medico/api/v0/find/services?healthService=6082-ff-colonoscopia-total-hasta-ciego&specialty=cirugia-general-y-del-aparato-digestivo&province=madrid&city=&isSearchingByStreet=False&lat=0&lon=0&radiusInKm=0&userLatitude=0.4166&userLongitude=-0.7003&resultsPerPage=30&keyword=&orderBy=price&page=