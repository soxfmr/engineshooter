import json
import scrapy
from engine import GoogleEngine
try:
    import winsound
except Exception as e:
    print e


class EngineShooterSpider(scrapy.Spider):
    name = 'engineshooter'
    handle_httpstatus_list = [301, 302, 503]

    def __init__(self, keyword, engine='g', maxpage=0, *args, **kwargs):
        self.engine = None
        self.keyword = keyword
        self.maxpage = maxpage
        super(EngineShooterSpider, self).__init__(*args, **kwargs)

        if not keyword:
            raise ValueError('argument keyword should be provides')

        # if engine == 'g':
        #     self.engine = GoogleEngine(self)
        # Only Google engine implements
        self.engine = GoogleEngine(self)

    def start_requests(self):
        yield self.engine.search(self.keyword, self.parse, self.maxpage)

    def parse(self, response):
        if not self.engine.parse(response):
            if self.engine.intercept():
                try: winsound.Beep(2500, 1000)
                except:pass
        else:
            # Retrieve result url
            # results = engine.get_result_url()
            #
            # Retrieve all information
            # results = engine.get_result()

            # Retrieve all information
            results = self.engine.get_result()
            for item in results:
                yield item

        yield self.engine.next()
