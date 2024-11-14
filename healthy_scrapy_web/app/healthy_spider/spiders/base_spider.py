# -*- coding: utf-8 -*-
import re
import scrapy
import urllib.parse


class BaseScrape(scrapy.Spider):

    def re_get_price(self, content):
        """
        Get number with or with out comma or point
        :param str content: Text where the number is in
        :rtype: str
        """
        try:
            return re.compile(r'(?:[+-]|\()?\$?\d+(?:,\d+)*(?:\.\d+)?\)?').search(content).group(0)
        except:
            return ''

    def re_replace_multi_jump_line(self, content):
        """
        Replace multi continuous jump line "\n", more than one
        :param str content: Text to regex
        :rtype: str
        """
        return re.sub(r'(\n){2,}', '\n', content)

    def get_complete_url_with_params(self, url, params):
        """
        join url (domain) and params passed by dict with a "?" in the middle.
        :param str url: domain
        :param dict params: dictionary of params
        :return: domain (url) + '?' + params
        :rtype: str
        """
        return urllib.parse.urljoin(url, '?'+urllib.parse.urlencode(params))
