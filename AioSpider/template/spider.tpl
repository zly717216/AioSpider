from AioSpider.spider import Spider


class {{ name_en }}Spider(Spider):

    name = '{{ name }}'
    source = '{{ source }}'
    start_urls = {{ start_urls }}
    target = '{{ target }}'

    def parse(self, response):
        pass


if __name__ == '__main__':
    spider = {{ name_en }}Spider()
    spider.start()
