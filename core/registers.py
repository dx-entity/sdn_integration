from modules import ModuleInterface


class Registers(object):
    _instance = None

    def __init__(self):
        self.module = {}
        pass

    @staticmethod
    def get_instance():
        if not Registers._instance:
            Registers._instance = Registers()
        return Registers._instance

    def register_module(self, name, obj):
        if not isinstance(obj, ModuleInterface):
            print "do something, not an instance of modules"
            return False
        if type(name) != type(''):
            print "name is not str"
            return False
        self.module[name] = obj


def register_module_access(module_name):
    register = Registers.get_instance()
    
    def _register_module_access(cls):
        flag = register.register_module(module_name, cls())
        cls.registered = flag
        return cls
    return _register_module_access
