import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlencode
import datetime
import csv




class ComicBooksSpider(scrapy.Spider):
    #Spider Name
    name='ComicBooksSpider'
    
    #Base URL
    base_url='https://www.yelp.com/'
    
    #Search Query Parameters
    params={
        'find_desc':'Comic Books',
        'find_loc':''
    }
    
    #Headers
    headers={
     'User-Agent': "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    
    #Custom Download Settings
    custom_settings={
        'CONCURRENT_REQUESTS_PER_DOMAIN':1,
        'DOWNLOAD_TIMEOUT':3    #250ms of delay
    }
    
    
    cities=[]
    
    # constructor
    def __init__(self):
        # opening the CSV file
        with open('yelpScraper/spiders/uscities.csv', mode ='r')as file:
            # reading the CSV file
            csvFile = csv.reader(file)
            # displaying the contents of the CSV file
            for lines in csvFile:
                self.cities.append(lines[0])
        
        self.cities.remove('city')
    
    def combineList(l):
        if len(l)==0:
            return None
        else:
            content=''
            for item in l:
                content+=str(item)+" "
            return content
    
    #Spider
    def start_requests(self):
        filename='./output/commercial_Sale_'+datetime.datetime.now().strftime("%H:%M:%S")
        #creating URL for cities
        for city in self.cities:
            self.params['find_loc']=city
            url=self.base_url+'search?'+urlencode(self.params)
            yield scrapy.Request(url=url,headers=self.headers,callback=self.parse_all_stores)
            break
    
    #parse indivisual store
    def parse_all_stores(self,response):
        links=response.xpath("//h3[@class='css-1agk4wl']/span/a/@href").extract()
        for link in links:
            yield response.follow(url=link,headers=self.headers,callback=self.parse_store)
            break

    def parse_store(self,response):
        
        bName=response.xpath("//h1/text()").extract_first(),
        priBCat=response.xpath("//span[contains(@class,' css-1fdy0l5')]/a/text()").extract(),
        bLine1=response.xpath("//address/following-sibling::p/text()").extract()
        bLine2=response.xpath("//address/p[last()]/span/text()").extract_first()
        phone=response.xpath("//p[@class=' css-na3oda']/following-sibling::p/text()").extract_first()
       
        
        yield{
            'Business Name':bName,
            'Primary Business Category':priBCat,
            'Business Address Line 1 (street address)':bLine1,
            'Business Address Line 2':bLine2,
            'Phone No':phone
        }

if __name__=='__main__':
    #run scraper
    process=CrawlerProcess()
    process.crawl(ComicBooksSpider)
    process.start()
    
    
    
    
    
            
        # bName=response.xpath("//h1/text()").extract_first(),
        # priBCat=self.combineList(response.xpath("//span[contains(@class,' css-1fdy0l5')]/a/text()").extract()),
        # bLine1=response.xpath("//address/p/a/span/text()").extract_first()+' '+self.combineList(response.xpath("//address/following-sibling::p/text()").extract())
        # bLine2=response.xpath("//address/p[last()]/span/text()").extract_first()
        # phone=response.xpath("//p[@class=' css-na3oda']/following-sibling::p/text()").extract_first()