import sys
sys.path.append('/root/parabola')
from apps.parabola.test.config_test.config_init import *

CONF(default_config_files=['../config.conf'])

print CONF.OVS_CONTAINER.ip
print CONF.of_controller