from AioSpider.middleware import Middleware


class ${project.upper}Middleware(Middleware):
    """爬虫中间件"""

    def process_request(self, request):
        """
            处理请求
            @params:
                request: Request 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """
        return None

    def process_response(self, response):
        """
            处理请求
            @params:
                response: Response 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """
        return None

    def process_exception(self, request, exception):
        """
            处理请求
            @params:
                request: Request 对象
            @return:
                Request: 交由引擎重新调度该Request对象
                Response: 交由引擎重新调度该Response对象
                None: 正常，继续往下执行 穿过下一个中间件
                False: 丢弃该Request或Response对象
        """
        return None
