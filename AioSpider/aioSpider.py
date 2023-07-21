import sys
from typing import List

from AioSpider.cmd import (
    ArgsP, ArgsS, ArgsI, ArgsO, ArgsH, OptionsU,
    OptionsEn, OptionsS, OptionsT, OptionsD
)
from AioSpider.cmd.cmd import (
    CommandName, HelpCommand, ListCommand, VirsionCommand
)
from AioSpider.cmd.make import MakeCommand
from AioSpider.cmd.create import CreateCommand
from AioSpider.cmd.test import TestCommand
from AioSpider.cmd.server import ServerCommand


class Client:

    def __init__(self, argv: List[str]):
        self._validate_args(argv)
        command = self._get_command(argv[1])
        args, options, names = self._parse_options_and_names(argv[2:])
        self._add_options_to_command(command, options)
        self._add_args_to_command(command, args)
        self._add_names_to_command(command, names)
        command.execute()

    def _validate_args(self, argv: List[str]):
        if (not isinstance(argv, list)) or (len(argv) <= 1) or (argv[0] != 'aioSpider'):
            print(f'aioSpider command error, aioSpider {ArgsH()} 查看帮助')

    def _get_command(self, cmd_name: str):
        command_mapping = {
            'create': CreateCommand,
            'make': MakeCommand,
            'list': ListCommand,
            'test': TestCommand,
            '-h': HelpCommand,
            '-v': VirsionCommand,
            'server': ServerCommand,
        }
        try:
            return command_mapping[cmd_name]()
        except KeyError:
            raise Exception(f'aioSpider command error, aioSpider {ArgsH()} 查看帮助')

    def _parse_options_and_names(self, argv: List[str]):
        args = []
        options = []
        names = []

        for index, arg in enumerate(argv):
            if '--' not in arg:
                continue
            options.append((arg, argv[index + 1]))

        for arg, name in options:
            argv.remove(arg)
            argv.remove(name)

        for index, arg in enumerate(argv):
            if '-' not in arg:
                continue
            args.append((arg, argv[index + 1]))

        for arg, name in args:
            argv.remove(arg)
            argv.remove(name)

        for i in argv:
            names.append(i)

        return args, options, names

    def _add_args_to_command(self, command, args: List[tuple]):
        option_mapping = {
            '-p': ArgsP,
            '-h': ArgsH,
            '-s': ArgsS,
            '-i': ArgsI,
            '-o': ArgsO,
        }
        for arg, name in args:
            command.add_args(option_mapping[arg](name))

    def _add_options_to_command(self, command, options: List[tuple]):
        option_mapping = {
            '--u': OptionsU,
            '--en': OptionsEn,
            '--s': OptionsS,
            '--t': OptionsT,
            '--d': OptionsD,
        }
        for option, name in options:
            command.add_options(option_mapping[option](name))

    def _add_names_to_command(self, command, names: List[str]):
        for name in names:
            command.add_name(CommandName(name))


def main():
    argv = sys.argv
    argv[0] = argv[0].rstrip('.py').split('\\')[-1]
    Client(argv)


if __name__ == '__main__':
    # argv = sys.argv
    # argv = ['aioSpider', 'create', '-p', r'dddd']
    # argv = ['aioSpider', 'create', '-s', r'hello']
    # argv = ['aioSpider', 'server', 'run', '-h', '0.0.0.0', '-p', '10086']
    argv = ['aioSpider', 'server', 'stop', '-p', '10086']
    # argv = ['aioSpider', 'server', 'stop']
    # argv = ['aioSpider', 'stopServer']
    # argv = ['aioSpider', 'make', 'model', '-i', r'D:\companyspider\utils\table.txt']
    # argv = ['aioSpider', 'test', 'proxy', '-p', 'http://127.0.0.1:7890', '--d', '5']
    # argv = ['aioSpider', '-h']
    # argv = ['aioSpider', '-v']
    # argv = ['aioSpider', 'make', 'bat', '-o', r'D:\companyspider\utils\table.txt']
    # argv = ['aioSpider', 'make', 'spider', '-i', r'D:\companyspider\utils\curl.txt']
    Client(argv)
