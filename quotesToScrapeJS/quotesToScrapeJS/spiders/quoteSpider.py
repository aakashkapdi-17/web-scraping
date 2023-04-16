import scrapy
from scrapy_splash import SplashRequest 


class quoteSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
     'http://quotes.toscrape.com/js/'
        ]
        for url in urls:
            yield SplashRequest(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.xpath("//div[@class='quote']"):
            yield{
                'Quote Text':quote.xpath("span[@class='text']/text()").extract_first(),
                'author':quote.xpath("span/small/text()").extract_first(),
                'tags':quote.xpath("div[@class='tags']/a/text()").extract()
            }