import config_init
from oslo_log import log as logging

CONF = config_init.GetSingltonConf.get_conf()

def test():
    LOG = logging.getLogger(__name__)
    # CONF(default_config_files=["config.conf"])
    logging.register_options(CONF)
    logging.setup(CONF, 'parabola')
    CONF(default_config_files=["config.conf"])
    LOG.info("!@#@!#!@#!@")
    LOG.error("!@#@!#!@#!@")

test()