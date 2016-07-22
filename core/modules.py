from abc import ABCMeta, abstractmethod


class ModuleInterface(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass