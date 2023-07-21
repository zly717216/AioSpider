from abc import ABCMeta, abstractmethod


class AioSpiderOptions(metaclass=ABCMeta):
    """command options base class"""

    @abstractmethod
    def __init__(self, name=None):
        self.p = None
        self.name = name

    def __str__(self):
        return f'{self.p} {self.name}'

    __repr__ = __str__


class OptionsU(AioSpiderOptions):
    
    def __init__(self, name=None):
        self.p = '--u'
        self.name = name


class OptionsEn(AioSpiderOptions):

    def __init__(self, name=None):
        self.p = '--en'
        self.name = name


class OptionsS(AioSpiderOptions):

    def __init__(self, name=None):
        self.p = '--s'
        self.name = name
        

class OptionsT(AioSpiderOptions):

    def __init__(self, name=None):
        self.p = '--t'
        self.name = name
        
        
class OptionsD(AioSpiderOptions):

    def __init__(self, name=None):
        self.p = '--d'
        self.name = name
