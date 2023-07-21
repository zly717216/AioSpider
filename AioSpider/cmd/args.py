from abc import ABCMeta, abstractmethod


class AioSpiderArgs(metaclass=ABCMeta):
    """command options base class"""

    @abstractmethod
    def __init__(self, name=None):
        self.p = None
        self.name = name or ''

    def __str__(self):
        return f'{self.p} {self.name}'

    __repr__ = __str__


class ArgsP(AioSpiderArgs):
    def __init__(self, name=None):
        self.p = '-p'
        self.name = name or ''


class ArgsS(AioSpiderArgs):
    def __init__(self, name=None):
        self.p = '-s'
        self.name = name or ''


class ArgsI(AioSpiderArgs):
    def __init__(self, name=None):
        self.p = '-i'
        self.name = name or ''


class ArgsO(AioSpiderArgs):
    def __init__(self, name=None):
        self.p = '-o'
        self.name = name or ''


class ArgsH(AioSpiderArgs):
    def __init__(self, name=None):
        self.p = '-h'
        self.name = name or ''
