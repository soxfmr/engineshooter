import scrapy
from engine import GoogleEngine
try:
    import winsound
except Exception as e:
    print e


class EngineShooterSpider(scrapy.Spider):
    name = 'engineshooter'
    handle_httpstatus_list = [301, 302, 503]

    def start_requests(self):
        maxpage = getattr(self, 'max', 0)
        engine = getattr(self, 'engine', 'g')
        keyword = getattr(self, 'keyword', None)

        if not keyword:
            raise ValueError('argument keyword should be provides')

        if engine == 'g':
            e = GoogleEngine(self)

        yield e.search(keyword, self.parse, maxpage)

    def grab_captcha(self, response):
        engine = response.meta['engine']
        engine.grab_captcha(response)

    def parse(self, response):
        engine = response.meta['engine']
        if not engine.parse(response):
            if engine.intercept():
                try: winsound.Beep(2500, 1000)
                except:pass
        else:
            # Retrieve result url
            # results = engine.get_result_url()
            #
            # Retrieve all information
            # results = engine.get_result()

            # Retrieve all information
            results = engine.get_result()
            for item in results:
                yield item

        yield engine.next()
