import sys
import os
import ConfigParser


def get_app_list(app_config_path='apps/app_module.ini'):
    icr = IniConfigReader()
    app_dict = icr.analyse_config_file(app_config_path)
    return app_dict


class IniConfigReader:

    def __init__(self):
        self.analyse_res = {}

    def analyse_config_file(self, ini_file_path):
        if not os.path.exists(ini_file_path):
            raise NameError

        cf = ConfigParser.ConfigParser()
        cf.read(ini_file_path)

        section = cf.sections()
        for s in section:
            tmp = {}
            options = cf.options(s)
            for o in options:
                tmp[o] = cf.get(s, o)
            self.analyse_res[s] = tmp

        return self.analyse_res
