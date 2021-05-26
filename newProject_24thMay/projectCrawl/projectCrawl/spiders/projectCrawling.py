import scrapy
from pandas.core.common import flatten
from scrapy.crawler import CrawlerProcess

class PostsSpider(scrapy.Spider):
    name = "bugs"

    start_urls = [
       'https://github.com/nextcloud/android/issues'
    ]
    
    bugUrls = []
    
    custom_settings = {
        'CONCURRENT_REQUEST_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1
    }
   
    def parse(self, response):
        filename = 'all-bug-links.txt'
        self.bugUrls.append(response.css('.Box-row--focus-gray::attr(id)').getall())
        next_page = response.css('a.next_page::attr(href)').get()
        if next_page is not None:
           next_page = response.urljoin(next_page)
           yield scrapy.Request(next_page, callback=self.parse)
        flattened_bugUrls = self.flatten_list(self.bugUrls)
        with open(filename, 'w') as f:
                 f.write(str(flattened_bugUrls))
        for bugUrl in flattened_bugUrls:
            bugNumber = bugUrl.split('_')
            print('bugUrl !!!!!!!!!!!!', 'https://github.com/nextcloud/android/issues/'+ bugNumber[1])
            yield scrapy.Request('https://github.com/nextcloud/android/issues/'+ bugNumber[1], callback=self.parse_bugs)    
             
    def parse_bugs(self, response):
        bugNumber = response.xpath('//*[@id="partial-discussion-header"]/div[1]/div/h1/span[2]/text()')[0].get()
        if 'crash' in str(response.body).lower():
            with open('./downloadedBugs/bug' + bugNumber + '.html', 'wb') as f:
                 f.write(response.body)  

    def flatten_list(self, list):
        finalList = []
        for subList in list:
            print('from flatten_list() subList type!!!!!!!!!!1', subList[0])
            for item in subList:
                finalList.append(item)
        return finalList      

process = CrawlerProcess()
process.crawl(PostsSpider)
process.start()        