import AioSpider
from AioSpider.spider import Spider


class ${spider.upper}Spider(Spider):

    name = "${spider}"
    settings = {}
    start_urls = [${start_urls}]

    def parse(self, response):
        self.logger.info(response.text)


if __name__ == '__main__':
    spider = ${spider.upper}Spider()
    spider.start()
