
from abc import abstractmethod, ABCMeta

class BaseCleaner(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def clean_self(self):
        pass


class AgentCleaner(BaseCleaner):

    def __init__(self):
        pass


    def clean_self(self):
        pass


class EntryCleaner(BaseCleaner):

    def __init__(self):
        pass

    def clean_self(self):
        pass