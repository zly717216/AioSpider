from .request import Request


class FormRequest(Request):
    """ 实现POST请求 """

    def __init__(self, *args, **kwargs):
        formdata = kwargs.pop('data', None)
        if formdata and kwargs.get('method') is None:
            kwargs['method'] = 'POST'

        super(FormRequest, self).__init__(*args, **kwargs)

        if formdata:

            if isinstance(formdata, dict):
                query_str = [
                    (self.to_bytes(k, self.encoding), self.to_bytes(v, self.encoding)) for k, vs in formdata.items()
                    for v in (vs if hasattr(x, "__iter__") and not isinstance(vs, (str, bytes)) else [vs])
                ]
            else:
                query_str = formdata

            if self.method == 'POST':
                # 表单形式发送
                kwargs.setdefault(b'Content-Type', b'application/x-www-form-urlencoded')
                self._set_data(query_str) # 传递字符形式的 x-www-form-urlencoded
            else: # 如果不是POST请求 就默认是GET请求 那么久拼接查询字符串
                # 拼接网址
                self._set_url(self.url + ('&' if '?' in self.url else '?') + query_str)

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    # 工具函数 用在 request 里面 对参数data表单数据进行编码
    def to_bytes(self, data, encoding=None, errors='strict'):
        """
        返回“text”的二进制表示形式。如果“文本”已经是bytes对象，按原样返回。
        :param data: 传递的post数据
        :param encoding: 编码格式
        :param errors: encode函数的一个参数 设置不同错误的处理方案。默认为 'strict',意为编码错误引起一个UnicodeError。
        :return: 返回字节形式的数据(经过了编码)
        """
        if isinstance(data, bytes):
            return data
        # 如果数据不是字符串形式的就报错
        if not isinstance(data, str):
            raise TypeError(f'to_bytes 必须接受参数类型是: unicode, str 或者 bytes, 传递的是{type(data).__name__}')
        if encoding is None:
            encoding = 'utf-8'  # 默认是utf-8
        # 转化编码格式默认utf-8
        # errors --> 设置不同错误的处理方案。默认为 'strict',意为编码错误引起一个UnicodeError。
        return data.encode(encoding, errors)
