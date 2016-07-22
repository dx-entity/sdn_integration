import sys

sys.path.append('/root/parabola')

from ovs_manager.OvsManager import OvsManager
from apps.parabola.test.config_test.config_init import *

# ovs = get_ctl()

# print ovs.db_find('port', ['name','p10']).execute()


CONF(default_config_files=['../config.conf'])
o = OvsManager.get_instance()
o.add_container(CONF.OVS_CONTAINER.ip, CONF.OVS_CONTAINER.port)
container = o.get_container(CONF.OVS_CONTAINER.ip)
print container.br_list
s3 = container.get_br('s1')
print s3.port_list
print s3.static
s3_eth3 = s3.get_port('s1-eth1')
print s3_eth3.interface_list
print s3_eth3.static
inter_s3 = s3_eth3.get_interface('s1-eth1')
print inter_s3.static
# br.add_port('p10', port_type=data.VXLAN, vxlan_remote_ip='192.168.0.1')
# print '1'
# br.add_port('p11')
# print '2'
# print br.get_port('p11')

# from neutron.agent.ovsdb.impl_vsctl import OvsdbVsctl





