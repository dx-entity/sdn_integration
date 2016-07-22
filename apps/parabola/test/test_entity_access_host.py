import sys
sys.path.append('/root/parabola')

from entity_access.EntityAccess import EntityAccess
from entity_access.EntityAccess import AgentConfig

entity_gate = '172.16.21.144'

ea = EntityAccess(entity_gate=entity_gate)
ea.add_agent_access_br(br_name='br_access',patch_port_name='patch_port4',vlan_id='100', remote_port_name='vxlan_port4', vxlan_key='456', agent_ip='172.16.18.233')

agent = AgentConfig(agent_ip='172.16.18.233')

agent.access_port(access_br='s1', entity_gate=entity_gate, access_port='access_vxlan', vxlan_key='456')