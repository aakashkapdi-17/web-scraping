import scrapy
from ..items import QuotestoscrapeItem

class QuoteSpider(scrapy.Spider):
    name='Quotes'
    start_urls=[f'https://quotes.toscrape.com/page/{i}/' for i in range(1,11)]
    
    def parse(self, response):
        
        item=QuotestoscrapeItem()
        title=response.xpath('//a[normalize-space()="Quotes to Scrape"]/text()').extract()
        yield {'title':title}
        quotes=response.xpath('//div[@class="quote"]')

        for quote in quotes:
            item['text']=quote.xpath("span[@class='text']/text()").extract_first()
            item['author']=quote.xpath("span[2]/small/text()").extract_first()
            item['tags']=quote.xpath("div/a/text()").extract()
            
            yield item
