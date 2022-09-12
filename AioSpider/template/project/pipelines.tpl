from AioSpider.pipelines import Pipeline, CSVFilePipeline


class ${project.upper}Pipeline(Pipeline):
    """数据处理管道"""

    def spider_open(self):
        """spider opened enter"""
        pass

    def spider_close(self):
        """spider closed enter"""
        pass

    def process_item(self, item):
        """yield item enter"""
        return item


class ${project}CSVPipeline(CSVFilePipeline):
    """CSV数据处理管道"""

    model = '${project}Model'
