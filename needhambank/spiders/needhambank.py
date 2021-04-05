import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from needhambank.items import Article


class needhambankSpider(scrapy.Spider):
    name = 'needhambank'
    start_urls = ['https://www.needhambank.com/about-us/news']

    def parse(self, response):
        links = response.xpath('//a[@class="Learn-More"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="Next "]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="publishDate Property"]/text()').get()
        if date:
            date = date.strip()
        else:
            return

        content = response.xpath('//div[@class="Body"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
