class ConfigError(Exception):

    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super(ConfigError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.msg}'

    def __repr__(self):
        return str(self)


class SystemConfigError(ConfigError):

    ERR_MAP = {
        'AioSpiderPath': '系统配置中AioSpiderPath未配置',
        'BackendCacheEngineError': '系统配置中BackendCacheEngine未配置或配置错误'
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):

        if msg is None:
            if flag == 1:
                msg = self.ERR_MAP['AioSpiderPath']
            elif flag == 2:
                msg = self.ERR_MAP['BackendCacheEngineError']
            else:
                msg = ''

        self.msg = msg
        super(SystemConfigError, self).__init__(msg, *args, **kwargs)


class RequestError(Exception):
    
    ERR_MAP = {
        'MethodType': '请求方法不正确，AioSpider 只支持 GET 和 POST 请求',
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):
        
        if msg is None:
            
            if flag == 0:
                msg = self.ERR_MAP['MethodType']
            else:
                msg = ''

        self.msg = msg
        super(RequestError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}<{self.msg}>'

    def __repr__(self):
        return str(self)


class ProxyError(Exception):
    
    ERR_MAP = {
        'NoIp': '没有可用的IP',
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):
        
        if msg is None:
            
            if flag == 0:
                msg = self.ERR_MAP['NoIp']
            else:
                msg = ''

        self.msg = msg
        super(ProxyError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}<{self.msg}>'

    def __repr__(self):
        return str(self)
    
    
class NoRedisServerError(Exception):
    
    ERR_MAP = {
        'NoServer': '没有找到 Redis Server',
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):
        
        if msg is None:
            
            if flag == 0:
                msg = self.ERR_MAP['NoServer']
            else:
                msg = ''

        self.msg = msg
        super(NoRedisServerError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}<{self.msg}>'

    def __repr__(self):
        return str(self)
    
    
class MiddlerwareError(Exception):
    
    ERR_MAP = {
        'request_return_error': '中间件返回值错误，中间件的process_request方法返回值必须为 Request/Response/None/False 对象',
        'response_return_error': '中间件返回值错误，中间件的process_response方法返回值必须为 Request/Response/None/False 对象',
        'exception_return_error': '中间件返回值错误，中间件的process_exception方法返回值必须为 Request/Response/None/False 对象',
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):
        
        if msg is None:
            
            if flag == 0:
                msg = self.ERR_MAP['request_return_error']
            elif flag == 1:
                msg = self.ERR_MAP['response_return_error']
            elif flag == 2:
                msg = self.ERR_MAP['exception_return_error']
            else:
                msg = ''
                
        self.msg = msg
        super(MiddlerwareError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}<{self.msg}>'

    def __repr__(self):
        return str(self)


class SqlError(Exception):
    
    ERR_MAP = {
        'index_error': '指定的索引太长；最大最大长度为767字节',
    }

    def __init__(self, msg: str = None, flag: int = 0, *args, **kwargs):

        if msg is None:

            if flag == 0:
                msg = self.ERR_MAP['index_error']
            else:
                msg = ''

        self.msg = msg
        super(SqlError, self).__init__(msg, *args, **kwargs)

    def __str__(self):
        return f'{self.__class__.__name__}<{self.msg}>'

    __repr__ = __str__

