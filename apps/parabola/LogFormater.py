from oslo_log import log as logging
from config_init import GetSingletonConf

CONF = GetSingletonConf.get_conf()

logging.register_options(CONF)
logging.setup(CONF, 'parabola')


def get_logger(name):
    return logging.getLogger(name)
