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
    
    def start_requests(self):
        yield scrapy.Request(url="https://www.classcentral.com/subjects",headers=self.headers,callback=self.parse)
    
    def parse(self, response):
        for subject in response.xpath("//ul[@class='filter-tabs__list']/li"):
            subject_name=subject.xpath("a/text()").extract()
            subject_url=subject.xpath("a/@href").extract_first()
            if subject_url is None:
                subject_name='computer-science'
                subject_url=response.url
                yield response.follow(url=subject_url,headers=self.headers,meta={'subject_name':subject_name},callback=self.scrapeTopics)
            else:
                subject_name=subject_name[-1].strip()
                print(subject_name,subject_url)
                yield response.follow(url=subject_url,headers=self.headers,meta={'subject_name':subject_name},callback=self.scrapeTopics)
        

    def scrapeTopics(self,response):
        subject_name=response.meta.get('subject_name')
        for topic in response.xpath("//ol[contains(@class,'list-no-style l-subjects-page__subjects-list')]/li"):
            topic_url=topic.xpath("a/@href").extract_first()
            topic_name=topic.xpath("a/span[1]/text()").extract_first()
            yield response.follow(url=topic_url,headers=self.headers,meta={'subject_name':subject_name,'topic_name':topic_name},callback=self.scrapeCourses)
            
        
    def scrapeCourses(self,response):
        subject_name=response.meta.get('subject_name')
        topic_name=response.meta.get('topic_name')
        for course in response.xpath("//li[contains(@class,'course-list-course')]"):
            course_details_url=course.xpath("div/p/a/@href").extract_first()
            yield response.follow(url=course_details_url,headers=self.headers,meta={'subject_name':subject_name,'topic_name':topic_name},callback=self.scrapeCourseDetails)
            
    
    def scrapeCourseDetails(self,response):
        subject_name=response.meta.get('subject_name')
        topic_name=response.meta.get('topic_name')
        
        course_title=response.xpath("//h1/text()").extract_first()
        course_institute=response.xpath("//h1/following-sibling::p/a/text()").extract_first()
        course_platform=response.xpath("//h1/following-sibling::p/span/a/text()").extract_first()
        course_enrollment=response.xpath("//nav[contains(@class,'course-header')]/ul/li[1]//strong/text()").extract_first()
        course_language=response.xpath("//div[@id='details-contents']/ul/li/div//span[contains(text(),'Languages')]/parent::div/following-sibling::div/a/text()").extract_first()
        course_subtitles=response.xpath("//div[@id='details-contents']/ul/li/div//span[contains(text(),'Subtitles')]/parent::div/following-sibling::div/span/text()").extract_first()
        course_instructors=response.xpath("//h3[contains(text(),'Taught')]/following-sibling::*/text()").extract()
        course_rating=response.xpath("//div[@id='reviews-contents']/div/p/strong/text()").extract_first()
        course_description=response.xpath("//div[contains(@data-truncatable-id,'content')]/text()").extract()
        course_link=response.url

        yield{
            'Subject':subject_name.strip() if subject_name is not None else None,
            'Topic':topic_name.strip() if topic_name is not None else None,
            'Course Title':course_title.strip() if course_title is not None else None,
            'Course Institute':course_institute.strip() if course_institute is not None else None,
            'Course Platform':course_platform.strip() if course_platform is not None else None,
            'Course Enrollment':course_enrollment.strip() if course_enrollment is not None else None,
            'Course Language':course_language.strip() if course_language is not None else None,
            'Course Rating':course_rating.strip() if course_rating is not None else None,
            'Course Subtitle':' '.join(course_subtitles.split()) if course_subtitles is not None else None,
            'Course Instructors':[' '.join(item.split()) for item in course_instructors if ' '.join(item.split()) is not ''] if course_instructors is not None else None, 
            'Course Description':[' '.join(item.split()) for item in course_description if ' '.join(item.split()) is not '' ] if course_description is not None else None,
            'Course Link':course_link
        }
        
