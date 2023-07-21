import time
import requests

from AioSpider.cmd.cmd import AioSpiderCommand, CommandName
from AioSpider.cmd.args import AioSpiderArgs, ArgsP, ArgsH
from AioSpider.cmd.options import AioSpiderOptions, OptionsU, OptionsD


class TestCommand(AioSpiderCommand):

    def execute(self):

        if self.command_name.name == 'proxy':
            self.test_proxy_bandwidth()
        else:
            raise Exception(f'command error, AioSpider test 没有该参数，AioSpider {ArgsH()} 查看帮助')

    def test_proxy_bandwidth(self):
        """
        测试ip带宽   aioSpider test proxy -p http://127.0.0.1:7890 --d 5 --u https://www.example.com/file/xxxx
        """

        proxy = None
        duration = 5
        url = 'https://797b822149c93a03ed0c1104e08a0f57.dlied1.cdntips.net/dldir1.qq.com/weixin/Windows/WeChatSetup' \
              '.exe?mkey=6454e52edfa67215&f=8f07&cip=223.166.84.224&proto=https&sche_svr=lego_ztc'

        for arg in self.args:
            if isinstance(arg, ArgsP):
                proxy = arg.name

        for opt in self.options:
            if isinstance(opt, OptionsU):
                url = opt.name
            if isinstance(opt, OptionsD):
                try:
                    duration = int(opt.name)
                except ValueError:
                    continue

        start_time = time.time()
        proxies = {'http': proxy, 'https': proxy}
        total_bytes = 0

        try:
            with requests.get(url, proxies=proxies, stream=True, timeout=duration) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    total_bytes += len(chunk)
                    elapsed_time = time.time() - start_time
                    if elapsed_time > duration:
                        break
        except requests.exceptions.RequestException as e:
            print(f"IP{proxy if proxy else '本机'} 测试失败，原因: {e}")
            return None

        print(f'测试成功：IP({proxy if proxy else "本机"})的带宽为 {total_bytes / elapsed_time / (1024 ** 2)} MB/s')

    def add_name(self, name: CommandName):
        self.command_name = name

    def add_args(self, args: AioSpiderArgs):
        self.args.append(args)

    def add_options(self, option: AioSpiderOptions):
        self.options.append(option)
