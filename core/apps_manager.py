import sys
import importlib

from core.modules import ModuleInterface


def load_apps(app_list):
    class_name = 'AppEntry'

    apps = []
    try:
        for key in app_list.keys():
            tmp = {}
            app = app_list[key]
            module_name = '.'.join(['apps', app['package_name'], 'register_app'])
            module = importlib.import_module(module_name)
            app_class = getattr(module, class_name)
            app_obj = app_class()
            if isinstance(app_obj, ModuleInterface):
                tmp[app['app_name']] = [app_obj, app['active']]
                apps.append(tmp)
    except ImportError, e:
        print e
        sys.exit(-1)
    return apps

