import scrapy
from ..items import YelpscraperItem
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
        'find_loc':'',
        'start':0
    }
    
    #Headers
    headers={
     'User-Agent': "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    
    #Custom Download Settings
    custom_settings={
        'CONCURRENT_REQUESTS_PER_DOMAIN':1,
        'DOWNLOAD_TIMEOUT':5,
        'FEEDS': { 'data.csv': { 'format': 'csv',}}   
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
        self.cities=self.cities[:10]
        
        # Output_headers = ['City','Business Name', 'Primary Business Category', 'Business Line 1', 'Business Line 2','Phone']
        # with open('comicBookOutput.csv', 'w', encoding='UTF8') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(Output_headers)
    
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
            yield scrapy.Request(url=url,headers=self.headers,meta={'city':city},callback=self.parse_all_pages,dont_filter=True)
      
    
    #parse indivisual store
    def parse_all_pages(self,response):
        city=response.meta.get('city')
        total_pages=response.xpath("//div[contains(@class,'pagination')]/div[2]/span/text()").extract_first().split(" ")[-1]
        index=[int(str(value)+'0') for value in range(0,int(total_pages))]
        for i in index:
            self.params['start']=i
            url=self.base_url+'search?'+urlencode(self.params)
            yield scrapy.Request(url=url,headers=self.headers,meta={'city':city},callback=self.parse_individual_page,dont_filter=True)
       
            
            
    def parse_individual_page(self,response):
        city=response.meta.get('city')
        links=response.xpath("//h3[@class='css-1agk4wl']/span/a/@href").extract()
        for link in links:
            yield response.follow(url=link,headers=self.headers,meta={'city':city},callback=self.parse_store)
    
            

    def parse_store(self,response):

        city=response.meta.get('city')
        bName=response.xpath("//h1/text()").extract_first(),
        priBCat=",".join(response.xpath("//span[contains(@class,' css-1fdy0l5')]/a/text()").extract()),
        bLine1=response.xpath("//address/p[1]//text()").extract_first()
        if response.xpath("//address/following-sibling::p/text()").extract_first():
            bLine1=bLine1+" "+ response.xpath("//address/following-sibling::p/text()").extract_first() 
        bLine2=" ".join(response.xpath("//address/p[last()]/span/text()").extract_first()),
        phone=response.xpath("//p[@class=' css-na3oda']/following-sibling::p/text()").extract_first()
        
        item=YelpscraperItem(City=city,Business_Name=bName,Business_Primary_Category= priBCat,
                             Business_Address_Line1 = bLine1,
                            Business_Address_Line2 = bLine2,
                             Phone = phone)
        yield item
                             
                             

             
        
if __name__=='__main__':
    #run scraper
    process=CrawlerProcess()
    process.crawl(ComicBooksSpider)
    process.start()