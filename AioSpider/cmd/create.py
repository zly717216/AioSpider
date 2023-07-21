import json
import shlex
import argparse
from pathlib import Path

from collections import OrderedDict
from urllib.parse import unquote, urlparse

from AioSpider.cmd.cmd import AioSpiderCommand, CommandName
from AioSpider.cmd.args import AioSpiderArgs, ArgsP, ArgsS, ArgsI, ArgsO, ArgsH
from AioSpider.cmd.options import AioSpiderOptions, OptionsU, OptionsEn, OptionsS, OptionsT
from AioSpider.template import gen_project
from AioSpider.template import gen_spider


class CurlToRequest:

    def __init__(self, curl_cmd):

        self._arguments = self.parse_args(self.curl_replace(curl_cmd))

        self._method = None
        self._url = None
        self._params = None
        self._data = None
        self._content_type = None
        self._headers = None
        self._cookies = None
        self._verify = None

    def parse_args(self, curl_cmd):

        parser = argparse.ArgumentParser()
        parser.add_argument('command')
        parser.add_argument('url')
        parser.add_argument('-d', '--data')
        parser.add_argument('-b', '--cookie', default=None)
        parser.add_argument('--data-binary', '--data-raw', '--data-ascii', default=None)
        parser.add_argument('-X', default='')
        parser.add_argument('-F', '--form', default=None)
        parser.add_argument('-H', '--header', action='append', default=[])
        parser.add_argument('-A', '--user-agent', default='')
        parser.add_argument('--compressed', action='store_true')
        parser.add_argument('-k', '--insecure', action='store_true')
        parser.add_argument('-I', '--head', action='store_true')
        parser.add_argument('-G', '--get', action='store_true')
        parser.add_argument('--user', '-u', default=())
        parser.add_argument('-i', '--include', action='store_true')
        parser.add_argument('-s', '--silent', action='store_true')

        cmd_set = shlex.split(curl_cmd)
        arguments = parser.parse_args(cmd_set)

        return arguments

    def curl_replace(self, curl_cmd):
        curl_replace = [
            (r'\\\r|\\\n|\r|\n', ''), (' -XPOST', ' -X POST'),
            (' -XGET', ' -X GET'), (' -XPUT', ' -X PUT'),
            (' -XPATCH', ' -X PATCH'), (' -XDELETE', ' -X DELETE'),
            (' -Xnull', ''), (r' \$', ' ')
        ]
        for pattern in curl_replace:
            curl_cmd = re.sub(pattern[0], pattern[1], curl_cmd)
        return curl_cmd.strip()

    def curl2request(self):

        output = 'import requests\n\n'
        req = ['response = requests.{}("{}"'.format(self.method, self.url)]

        if self.params:
            output += f"params = {self.prettier_dict_string(self.params)}\n\n"
            req.append('params=params')

        if self.data:
            if isinstance(self.data, dict):
                if 'application/json' in self.content_type:
                    output += f"data = json.dumps({self.prettier_dict_string(self.data)})\n\n"
                else:
                    output += f"data = {self.prettier_dict(self.data)}\n\n"
            else:
                output = 'from requests_toolbelt import MultipartEncoder\n' + output
                output += f"data = {self.prettier_dict(self.data)}\n\n"
            req.append('data=data')

        if self.headers:
            output += f"headers = {self.prettier_dict(self.headers)}\n\n"
            req.append('headers=headers')

        if self.cookies:
            output += f"cookies = {self.prettier_dict(self.cookies)}\n\n"
            req.append('cookies=cookies')

        if self.verify:
            req.append('verify=False')

        output += ', '.join(req) + ')\n\n'
        output += 'print(response.text)\n\n'

        return output

    def curl2aio(self):

        output = 'from AioSpider import tools\nfrom AioSpider.spider import Spider\n\n' \
                 f'from models import *\n\n\nclass DemoSpider(Spider):\n\n{" " * 4}name = "demoSpider"\n{" " * 4}' \
                 f'start_urls = [\n{" " * 8}"{self.url}"\n{" " * 4}]\n\n{" " * 4}def start_requests(self):\n{" " * 8}' \
                 f'for url in self.start_urls:\n{" " * 12}yield '
        output += "Request" if self.method.lower() == "get" else "FormRequest"
        output = (
                     "from AioSpider.http import Request\n" if self.method.lower() == "get"
                     else "from AioSpider.http import FormRequest\n"
                 ) + output
        output += f'(\n{" " * 16}url=url,\n'

        if self.headers:
            output += f"{' ' * 16}headers=" + self.prettier_dict(self.headers).replace('\n', f'\n{" " * 16}') + ',\n'

        if self.params:
            output += f"{' ' * 16}params={self.params},\n"

        if self.data:
            if isinstance(self.data, dict):
                if 'application/json' in self.content_type:
                    output += f"{' ' * 16}body={self.prettier_dict_string(self.data)},\n"
                else:
                    output += f"{' ' * 16}data={self.prettier_dict(self.data)},\n"
            else:
                output += f"{' ' * 16}data={self.prettier_dict(self.data)},\n"

        if self.cookies:
            output += f"{' ' * 16}cookies=" + self.prettier_dict(self.cookies).replace('\n', f'\n{" " * 16}') + '\n'

        output = output[:-1]
        output += f'\n{" " * 12})\n\n{" " * 4}def parse(self, response):\n{" " * 8}self.logger(response)\n\n\nif ' \
                  f'__name__ == "__main__":\n{" " * 4}spider = DemoSpider()\n{" " * 4}spider.start()'

        return output

    def prettier_dict(self, the_dict, indent=4):

        if not the_dict:
            return "{}"

        return f"\n{'' * indent}".join(
            json.dumps(the_dict, ensure_ascii=False, sort_keys=True, indent=indent, separators=(',', ': ')).splitlines()
        )

    def prettier_dict_string(self, item: dict, indent: int = 4):

        def quote(x):
            return f"'{x}'"

        if not item:
            return "{}"

        string = '{\n' + " " * indent
        string += f",\n{' ' * indent}".join(
            f"{quote(x) if isinstance(x, str) else str(x)}: {quote(y) if isinstance(y, str) else str(y)}"
            for x, y in item.items()
        )
        string += ',\n}'

        return string

    def parse_multi(self, the_data):

        boundary = b''

        if self.content_type:
            ct = self.parse_content_type()
            if not ct:
                return ['no content-type']
            try:
                boundary = ct[2]["boundary"].encode("ascii")
            except (KeyError, UnicodeError):
                return ['no boundary']

        if boundary:
            result = []
            for i in the_data.split(b"--" + boundary):

                p = i.replace(b'\\x0d', b'\r').replace(b'\\x0a', b'\n').replace(b'\\n', b'\n').replace(b'\\r', b'\r')
                parts = p.splitlines()

                if len(parts) > 1 and parts[0][0:2] != b"--":
                    if len(parts) > 4:
                        value = {}
                        key, value['filename'] = re.findall(br'\bname="([^"]+)"[^"]*filename="([^"]*)"', parts[1])[0]
                        value['content'] = b"".join(parts[3 + parts[2:].index(b""):])
                        value['content_type'] = parts[2]
                        value = (value['filename'].decode(), value['content'].decode(), value['content_type'].decode())
                    else:
                        key = re.findall(br'\bname="([^"]+)"', parts[1])[0]
                        value = (b"".join(parts[3 + parts[2:].index(b""):])).decode()
                    result.append((key.decode(), value))

            return result

    def parse_content_type(self):

        parts = self.content_type.split(';', 1)
        tuparts = parts[0].split('/', 1)

        if len(tuparts) != 2:
            return None

        dparts = OrderedDict()
        if len(parts) == 2:
            for i in parts[1].split(";"):
                c = i.split("=", 1)
                if len(c) == 2:
                    dparts[c[0].strip()] = c[1].strip()

        return tuparts[0].lower(), tuparts[1].lower(), dparts

    @property
    def url(self):
        if self._url is None:
            parse = urlparse(self._arguments.url)
            self._url = F"{parse.scheme}://{parse.netloc}{parse.path}"
        return self._url

    @property
    def method(self):
        if self._method is None:
            self._method = self._arguments.X.lower() if self._arguments.X else 'get'
        return self._method

    @property
    def params(self):
        if self._params is None:
            if urlparse(self._arguments.url).query:
                self._params = dict(re.findall(r'([^=&]*)=([^&]*)', unquote(urlparse(self._arguments.url).query)))
            else:
                self._params = ()
        return self._params

    @property
    def data(self):

        if self._data is None:

            post_data = self._arguments.data or self._arguments.data_binary

            if post_data and not self._arguments.get:
                self._method = 'post'
                if "multipart/form-data" in self.content_type.lower():
                    self._data = self.parse_multi(
                        unquote(post_data.strip('$')).encode('raw_unicode_escape')
                    )
                elif "application/json" in self.content_type.lower():
                    self._data = json.loads(post_data)
                else:
                    self._data = dict(re.findall(r'([^=&]*)=([^&]*)', unquote(post_data)))
            elif post_data:
                self._params = dict(re.findall(r'([^=&]*)=([^&]*)', unquote(post_data)))
                self._data = {}
            else:
                self._data = {}

        return self._data

    @property
    def content_type(self):
        if self._content_type is None:
            self._content_type = self.headers.get('Content-Type') or self.headers.get('content-type') or \
                                 self.headers.get('Content-type')
        return self._content_type

    @property
    def headers(self):
        if self._headers is None:
            if self._arguments.header:
                self._headers = dict([tuple(header.split(': ', 1)) for header in self._arguments.header])
            else:
                self._headers = {}
        return self._headers

    @property
    def cookies(self):

        if self._cookies is None:

            cookies = self._arguments.cookie if self._arguments.cookie else \
                self.headers.get('cookie') or self.headers.get('Cookie')

            if 'cookie' in self.headers:
                self.headers.pop('cookie')

            if 'Cookie' in self.headers:
                self.headers.pop('Cookie')

            if cookies:
                self._cookies = {cookie[0]: cookie[1] for cookie in re.findall(r'([^=\s;]*)=([^;]*)', cookies)}
            else:
                self._cookies = {}

        return self._cookies

    @property
    def verify(self):
        if self._verify is None:
            self._verify = True if self._arguments.insecure else False
        return self._verify


class CreateCommand(AioSpiderCommand):

    def execute(self):

        if self.args and isinstance(self.args[0], ArgsP):
            self.create_project(self.args[0].name)
        elif self.args and isinstance(self.args[0], ArgsS):
            self.create_spider(self.args[0].name)
        else:
            raise Exception(f'options error, AioSpider create 没有该参数，AioSpider {ArgsH()} 查看帮助')

    def create_project(self, name, settings=True):
        """创建项目: aioSpider create -p <name>"""

        if not name:
            raise NameError(
                f'aioSpider create -p <name>, Do you forget inout project name? AioSpider {ArgsH()} 查看帮助'
            )

        items = gen_project(name, settings=settings)

        if items is None:
            return True
        
        try:
            for item in items:
                if item['type'] == 'dir':
                    item['path'].mkdir(parents=True, exist_ok=True)
                else:
                    item['path'].write_text(item['text'], encoding='utf-8')
            return True
        except Exception:
            return False

    def create_spider(self, name, class_name=None):
        """创建爬虫 aioSpider create -s <name> --u start_url"""

        if name is None:
            raise Exception(
                f'aioSpider create -p <name>, Do you forget inout project name? AioSpider {ArgsH()} 查看帮助'
            )

        kw = {}
        for option in self.options:
            if isinstance(option, OptionsU):
                kw['start_urls'] = [option.name]
            if isinstance(option, OptionsEn):
                kw['name_en'] = option.name
            if isinstance(option, OptionsS):
                kw['source'] = option.name
            if isinstance(option, OptionsT):
                kw['target'] = option.name

        spider_text = gen_spider(name, **kw)
        
        if class_name is None:
            path = Path.cwd() / f'spider/{name}.py'
        else:
            path = Path.cwd() / f'spider/{class_name}/{name}.py'
            path.parent.mkdir(parents=True, exist_ok=True)

        try:
            path.write_text(spider_text, encoding='utf-8')
            return True
        except FileNotFoundError:
            return False

    def add_name(self, name: CommandName):
        self.command_name = name

    def add_args(self, args: AioSpiderArgs):
        self.args.append(args)

    def add_options(self, option: AioSpiderOptions):
        self.options.append(option)
