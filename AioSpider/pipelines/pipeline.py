class Pipeline:

    is_async = False

    def __init__(self, spider, *args, **kwargs):
        self.spider = spider
        self.logger = spider.logger

    def spider_open(self):
        pass

    def spider_close(self):
        pass

    def process_item(self, item):
        return item
