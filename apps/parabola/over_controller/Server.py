
import logging


class Serverbase(object):
    _instance = None

    @staticmethod
    def get_instance():
        if not Serverbase._instance:
            Serverbase._instance=Serverbase()

        return Serverbase._instance

    def __init__(self):
        # self.Log = logging.getLogger(self.__class__.__name__)
        pass

