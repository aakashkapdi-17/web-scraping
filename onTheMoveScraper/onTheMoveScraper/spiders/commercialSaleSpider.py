import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
import urllib
import datetime
import json

from scrapy_splash import SplashRequest 




class commercialSaleSpider(scrapy.Spider):
    
    #Spider Name
    name='commercialSaleSpider'
    
    #Base URL
    base_url='https://www.onthemarket.com/for-sale/property/'
    
    #Search Query Parameters
    params={
        'page':0,
        'radius':3.0
    }
    
    
    #Headers
    headers={
     'User-Agent': "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    
    #Custom Download Settings
    custom_settings={
        'CONCURRENT_REQUESTS_PER_DOMAIN':1,
        'DOWNLOAD_TIMEOUT':1    #250ms of delay
    }
    
    #current Page
    current_page=0
    
    #postcodes
    postcodes=[]
    
    #Constructor
    def __init__(self):
        
        #Converting postcodes to postcodes list
        with open('onTheMoveScraper\spiders\outcodes.csv','r') as f:
            self.postcodes=[line.strip().lower() for line in f if line.strip()]
        
        
    #General Crawler    
    def start_requests(self):
        filename='./output/commercial_Sale_'+datetime.datetime.now().strftime("%H:%M:%S")
        count=1
        
        #creating URL for postcodes
        for postcode in self.postcodes:
            next_postcode=self.base_url+postcode+'/?'+urllib.parse.urlencode(self.params)
            print(next_postcode)
            yield SplashRequest(url=next_postcode,headers=self.headers,meta={'postcode':postcode,'filename':filename,'count':count},callback=self.parse_links)
            count+=1
            break
    
    def parse_links(self, response):
        #Extract Forwarded Data
        postcode=response.meta.get('postcode')
        filename=response.meta.get('filename')
        count=response.meta.get('count')
        
        #info for debugging
        print('\n\nPOSTCODE %s:%s out of %s Postcodes' %(postcode,count,len(self.postcodes)))
        
        #loop over property cards
        for card in response.xpath("//li[@class='otm-PropertyCard']"):
            listings=card.xpath("div/div/div/a[@rel='nofollow']/@href").extract_first()
            listings="https://www.onthemarket.com"+listings
            print(listings)
            yield SplashRequest(url=listings,headers=self.headers,meta={'postcode':postcode,'filename':filename,'count':count},callback=self.parse_listings)
            break
        
        
    # parse indivisual property listings
    def parse_listings(self,response):
        #Extract Forwarded Data
        postcode=response.meta.get('postcode')
        filename=response.meta.get('filename')
        print(response.url)
        #extract features
        features={
            'id':response.url.split('/')[-2],
            'url':response.url,
            'postcode':postcode,
            'title':response.xpath("//h1/text()").extract_first(),
            'address':response.xpath("//h1/following-sibling::div[1]/text()").extract_first(),
            'price':response.xpath("//div[@class='otm-Price']/span/text()").extract_first(),
            'agent_name':response.xpath("//div[@class='agent-info-overview']//h2/text()").extract_first(),
            'agent_link':response.xpath("//div[@class='agent-info-overview']/a/@href").extract()[-1],
            'agent_address':response.xpath("//div[@class='agent-info-overview']//h2/following-sibling::p/text()").extract_first(),
            'agent_phone':response.xpath("//div[@class='property-action-label']/following-sibling::a/text()").extract_first(),
            'features':response.xpath("//section[@class='otm-FeaturesList mb-12']/ul/li/text()").extract(),
            'full_description':response.xpath("//div[@class='description-truncate']/div/text()").extract(),
        }
        
        pictureLink=response.url+"#/photos"
        print(pictureLink)
        yield scrapy.Request(url=pictureLink,headers=self.headers,meta={'postcode':postcode,'filename':filename},callback=self.parse_photos,dont_filter = True)
        
        print(json.dumps(features,indent=2))
        
    def parse_photos(self,response):
        print(response)
        
    
    
if __name__=='__main__':
    #run scraper
    process=CrawlerProcess()
    process.crawl(commercialSaleSpider)
    process.start()