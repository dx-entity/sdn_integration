import sys
sys.path.append('/root/parabola')

from entity_access.EntityAccess import EntityAccess
from entity_access.EntityAccess import AgentConfig
from global_view.global_statics import get_global

entity_gate = '172.16.21.144'

ea = EntityAccess(entity_gate=entity_gate)
ea.add_agent_access_br(br_name='br_access1', patch_port_name='patch_port1', vlan_id='400', remote_port_name='vxlan_port1', agent_ip='172.16.18.233', vxlan_key='123')
ea.add_agent_access_br(br_name='br_access2', patch_port_name='patch_port2', vlan_id='500', remote_port_name='vxlan_port2', agent_ip='172.16.18.233', vxlan_key='234')
ea.add_agent_access_br(br_name='br_access', patch_port_name='patch_port3', vlan_id='100', remote_port_name='vxlan_port3', vxlan_key='456', agent_ip='172.16.18.233')

#
agent = AgentConfig(agent_ip='172.16.18.233')
#
agent.access_port(access_br='s2', entity_gate=entity_gate, access_port='access_vxlan1', vxlan_key='123')
agent.access_port(access_br='s3', entity_gate=entity_gate, access_port='access_vxlan2', vxlan_key='234')
agent.access_port(access_br='s2', entity_gate=entity_gate, access_port='access_vxlan3', vxlan_key='456')
# agent.access_port(access_br='s3', entity_gate=entity_gate, access_port='access_vxlan2')


get_global()