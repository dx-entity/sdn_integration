from main import main
from core.modules import ModuleInterface


class AppEntry(ModuleInterface):
    def __init__(self):
        pass

    def start(self):
        print "%s start." % (self.__class__.__name__)
        main()

    def stop(self):
        pass