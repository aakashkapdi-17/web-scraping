import scrapy
from scrapy.crawler import CrawlerProcess



class ClassCentralSpider(scrapy.Spider):
    name = "ClassCentralSpider"
    allowed_domains = ["classcentral.com"]
   
    #Headers
    headers={
     'User-Agent': "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }

    #Custom Download Settings
    custom_settings={
        'CONCURRENT_REQUESTS_PER_DOMAIN':1,
        'DOWNLOAD_TIMEOUT':10    #250ms of delay
    }
    

    # def __init__(self, subject=None):
    #     self.subject=subject
    

    def start_requests(self):
        yield scrapy.Request(url="https://www.classcentral.com/subjects",headers=self.headers,callback=self.parse)
    
    def parse(self, response):
        for subject in response.xpath("//ul[@class='filter-tabs__list']/li"):
            subject_name=subject.xpath("a/text()").extract()
            subject_url=subject.xpath("a/@href").extract_first()
            if subject_url is None:
                continue
                # subject_name='computer-science'
                # subject_url=response.url
                # yield response.follow(url=subject_url,headers=self.headers,meta={'subject_name':subject_name},callback=self.scrapeTopics,)

            else:
                subject_name=subject_name[-1].strip()
                print(subject_name,subject_url)
                yield response.follow(url=subject_url,headers=self.headers,meta={'subject_name':subject_name},callback=self.scrapeTopics)
            break
        

    def scrapeTopics(self,response):
        subject_name=response.meta.get('subject_name')
        for topic in response.xpath("//ol[contains(@class,'list-no-style l-subjects-page__subjects-list')]/li"):
            topic_url=topic.xpath("a/@href").extract_first()
            topic_name=topic.xpath("a/span[1]/text()").extract_first()
            yield response.follow(url=topic_url,headers=self.headers,meta={'subject_name':subject_name,'topic_name':topic_name},callback=self.scrapeCourses)
            break
        
    def scrapeCourses(self,response):
        subject_name=response.meta.get('subject_name')
        topic_name=response.meta.get('topic_name')
        for course in response.xpath("//li[contains(@class,'course-list-course')]"):
            course_details_url=course.xpath("div/p/a/@href").extract_first()
            yield response.follow(url=course_details_url,headers=self.headers,meta={'subject_name':subject_name,'topic_name':topic_name},callback=self.scrapeCourseDetails)
            
    
    def scrapeCourseDetails(self,response):
        topic_name=response.meta.get('subject_name')
        topic_name=response.meta.get('topic_name')
        
        course_title=response.xpath("//h1/text()").extract_first()
        course_institute=response.xpath("//h1/following-sibling::p/a/text()").extract_first()
        course_platform=response.xpath("//h1/following-sibling::p/span/a/text()").extract_first()
        course_enrollment=response.xpath("//nav[contains(@class,'course-header')]/ul/li[1]//strong/text()").extract_first()
        course_language=response.xpath("//div[@id='details-contents']/ul/li[3]/div[last()]/a/text()").extract_first()
        course_subtitles=response.xpath("//div[@id='details-contents']/ul/li[7]/div[last()]/span/text()").extract_first()
        course_instructors=response.xpath("//div[@id='reviews-contents']/div/p/strong/text()").extract()
        course_description=response.xpath("//div[contains(@data-truncatable-id,'content')]/text()").extract()

        yield{
            'Subject':topic_name,
            'Topic':topic_name,
            'Course Title':course_title,
            'Course Institute':course_institute,
            'Course Platform':course_platform,
            'Course Enrollment':course_enrollment,
            'Course Language':course_language,
            'Course Subtitle':course_subtitles,
            'Course Instructors':course_instructors,
            'Course Description': course_description,
        }
        
if __name__=='__main__':
    #run scraper
    process=CrawlerProcess()
    process.crawl(ClassCentralSpider)
    process.start()