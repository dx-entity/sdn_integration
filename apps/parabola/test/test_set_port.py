import sys
sys.path.append('/root/parabola')

from ovs_manager.OvsManager import OvsManager
from apps.parabola.test.config_test.config_init import *
import static as data


CONF(default_config_files=['../config.conf'])
o = OvsManager.get_instance()
print CONF.OVS_CONTAINER.ip
o.add_container(CONF.OVS_CONTAINER.ip, CONF.OVS_CONTAINER.port)
container = o.get_container(CONF.OVS_CONTAINER.ip)
br0 = container.get_br('br0')
br0.set_port('p1',port_type=data.TRUNK, trunk_permit='[2,3,5,6]')