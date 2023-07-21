import os
from pathlib import Path

from AioSpider import tools
from AioSpider import settings
from AioSpider.cmd.cmd import AioSpiderCommand, CommandName
from AioSpider.cmd.args import AioSpiderArgs, ArgsP, ArgsH
from AioSpider.cmd.options import AioSpiderOptions


class ServerCommand(AioSpiderCommand):

    def execute(self):

        if self.command_name.name == 'run':
            self.run_server()
        elif self.command_name.name == 'stop':
            self.stop_server()
        else:
            raise Exception(f'command error, AioSpider server 没有该参数，AioSpider {ArgsH()} 查看帮助')

    def run_server(self):
        """
        启动节点服务器   aioSpider server run -h 0.0.0.0 -p 10086
        """

        cwd = Path.cwd()

        port = None
        host = None

        for arg in self.args:
            if isinstance(arg, ArgsH):
                host = arg.name
            if isinstance(arg, ArgsP):
                port = arg.name
                
        if port is None:
            port = settings.ServerConfig.slaver['port']
            
        if host is None:
            host = settings.ServerConfig.slaver['host']

        os.chdir(Path(__file__).parent.parent / 'server')
        pid = tools.start_cmd(f'uvicorn main:app --host {host} --port {port}', close=True)
        os.chdir(cwd)

        print(f'{host}:{port} 启动成功：IPV4: {tools.get_ipv4()}')
        
    def stop_server(self):
        """
        关闭节点服务器   aioSpider server stop -p 10086
        """

        port = None

        for arg in self.args:
            if isinstance(arg, ArgsP):
                port = arg.name

        if port is None:
            port = settings.ServerConfig.slaver['port']

        tools.close_program_by_port(port)
        print(f'{tools.get_ipv4()}服务器关闭成功')

    def add_name(self, name: CommandName):
        self.command_name = name

    def add_args(self, args: AioSpiderArgs):
        self.args.append(args)

    def add_options(self, option: AioSpiderOptions):
        self.options.append(option)
