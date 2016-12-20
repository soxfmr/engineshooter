# -*- coding: utf-8 -*-
import re
import os
import scrapy
import random
import string
import tempfile
import webbrowser
from os.path import join
from urllib import urlencode
from StringIO import StringIO
from engineshooter.items import SearchResultItem


class GoogleEngine:
    name = 'google'

    BASE_URL = 'https://www.google.com/search?q={}&num=100'
    CAPTCHA_URL = 'https://ipv4.google.com/sorry/index'

    NOTHING_MATCHES_TAG = ('<div class="mnr-c">', 'did not match any documents.', 'Suggestions:')

    def __init__(self, spider):
        self.spider = spider
        self.keyword = ''
        self.callback = None
        self.maxpage = 0
        self.result = []
        self.intercept_status = False
        self.url_next_page = None
        self.request = None
        self.payload = None
        self.current_page = 0

    def search(self, keyword, callback, maxpage=0):
        self.maxpage = maxpage
        self.keyword = keyword
        self.callback = callback

        return scrapy.Request(url=GoogleEngine.BASE_URL.format(self.keyword), callback=self.callback)

    def parse(self, response):
        # reset
        self.request = None
        self.result = []
        self.url_next_page = None
        self.intercept_status = False

        # Nothing found
        empty = True
        for tag in GoogleEngine.NOTHING_MATCHES_TAG:
            if tag not in response.body:
                empty = False
                break
        if empty:
            self.spider.logger.warning('Empty search result')
            return False

        # Determine whether the captcha present
        if response.status in [301, 302]:
            if GoogleEngine.CAPTCHA_URL in response.headers['Location']:
                self.spider.logger.info(response.headers['Location'])
                self.spider.logger.warning('Captcha redirect detect, grabing the captcha...')
                self.request = scrapy.Request(url = response.headers['Location'], callback = self.callback,
                    dont_filter = True, meta = {'route' : self.grab_captcha})
            else:
                if 'route' not in response.meta:
                    # Validate success
                    self.spider.logger.info('Validate success, continue for next request')
                self.url_next_page = response.headers['Location']
            return False

        if response.status in [503] or 'route' in response.meta:
            '''
            self.spider.logger.warning('Validation code incorrectly, please retry')
            self.request = scrapy.Request(url = response.url, callback = self.callback,
                dont_filter = True, meta = {'engine' : self, 'route' : self.grab_captcha})
            '''
            response.meta['route'](response)
            return False

        # Extact all of result
        for item in response.css('h3.r'):
            try:
                result = SearchResultItem()
                result['url'] = re.search('http[s]*://.+', item.css('a::attr(href)').extract_first()).group()
                # Right to Left
                title = item.css('a::text').extract_first() or item.css('a span::text')
                if not title:
                    title = ''

                result['title'] = title.encode('utf-8')
                self.result.append(result)
            except Exception as e:
                self.spider.logger.error('An error occured when extract the item: ' + str(e))

        # Current page
        current_page = response.css('td.cur::text').extract_first()
        if current_page:
            self.current_page = int(current_page)
            self.spider.logger.info('Current search index %d', self.current_page)

        # Parse next page information
        next_page = response.css('a#pnnext::attr(href)').extract_first()
        if next_page:
            next_page = re.sub('start=(\d+)', 'start=%d&num=100&' % (self.current_page * 100), next_page)
            self.url_next_page = response.urljoin(next_page)

        self.spider.logger.info('Totally %d urls been extracted from current page', len( self.result ))
        self.spider.logger.info('Response parsing completed')

        return True

    def next(self):
        if self.request:
            self.spider.logger.info('Urgent request provides, sending request directly.')
            return self.request

        if self.maxpage > 0 and self.current_page >= self.maxpage or self.url_next_page == None:
            self.spider.logger.info('Reached the end of page')
            return None

        self.spider.logger.info('Sending request for next page')
        return scrapy.Request(url = self.url_next_page, callback = self.callback, dont_filter = True)

    def grab_captcha(self, response):
        self.payload = {'q' : response.css('input[name=q]::attr(value)').extract_first().encode('utf-8'),
            'continue' : response.css('input[name=continue]::attr(value)').extract_first().encode('utf-8') }

        imgurl = response.urljoin(response.css('img::attr(src)').extract_first())
        self.request = scrapy.Request(url=imgurl, callback=self.callback, meta = {
            'route' : self.require_captcha, 'url' : response.url})
        # Notify user for captcha
        self.intercept_status = True

    def require_captcha(self, response):
        tmpdir = tempfile.gettempdir()
        path = join(tmpdir, ''.join(random.choice(string.letters + string.digits) for _ in range(6)) + '.jpg')
        with open(path, 'wb+') as handle:
            handle.write(response.body)

        webbrowser.open(path)
        while True:
            captcha = raw_input('Please enter the captcha: ')
            if not captcha:
                continue

            self.payload['captcha'] = captcha
            url = '{}?{}'.format(GoogleEngine.CAPTCHA_URL, urlencode(self.payload))

            self.spider.logger.info(url)

            self.request = scrapy.Request(url=url, dont_filter = True, meta = {'route' : self.grab_captcha})
            self.spider.logger.info(self.payload)
            break

        os.remove(path)

    def get_result_url(self):
        return map(lambda item: item['url'], self.result)

    def get_result(self):
        return self.result

    def intercept(self):
        return self.intercept_status
