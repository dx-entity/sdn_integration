
import eventlet

from core.apps_manager import load_apps

from utils.standard_config import get_app_list
from utils.global_data import GlobalData
from utils import statics as data


def main(*args, **kwargs):

    gd = GlobalData.get_instance()

    gd.app_info = load_apps(get_app_list())

    app_pool = eventlet.GreenPool()

    for app in gd.app_info:
        key = app.keys()[0]
        print 'installed: %s' % (app.keys()[0])
        active = app.get(key)[1]
        app_obj = app.get(key)[0]
        if active:
            app_pool.spawn(app_obj.start)
            gd.app_status[key] = data.App.status.RUNNING

    app_pool.waitall()

if __name__ == "__main__":
    main()