from apps.parabola.ovs_manager import OvsManager
import apps.parabola.static as data

BASE_BR_NAME='br_base'

ovs_manager = OvsManager.OvsManager.get_instance()


class EntityAccess(object):

    def __init__(self, entity_gate, interface=data.OVS.EntityAccess.INTERFACE, db_port=data.OVS.MANAGERPORT):
        self.entity_gate = entity_gate
        self.db_port = db_port
        self.out_port_name = interface
        self.base_container = None
        self.init_base_container()

    def init_base_container(self):
        if not ovs_manager.get_container(self.entity_gate):
            self.base_container = ovs_manager.add_container(self.entity_gate, self.db_port)[0]

        self.out_br = self.base_container.br_list.get(BASE_BR_NAME, None)
        if not self.out_br:
            self.out_br = self.base_container.add_br(BASE_BR_NAME)

        self.out_port = self.out_br.port_list.get(self.out_port_name, None)
        if not self.out_port:
            self.out_port = self.out_br.add_port(self.out_port_name, port_type=data.TRUNK,trunk_permit=data.OVS.EntityAccess.TRUNK)

    def add_agent_access_br(self, br_name=None, patch_port_name=None, remote_port_name=None, agent_ip=None, vxlan_key=None, vlan_id=None):
        br_exist = self.base_container.br_list.get(br_name, None)
        out_br_patch_name = patch_port_name + '_master'
        br_name = str(br_name)

        if not br_exist:
            access_br = self.base_container.add_br(br_name=br_name)
            if access_br:
                if not access_br.port_exist(port_name=patch_port_name):
                    access_br.add_port(patch_port_name, port_type=data.PATCH, patch_peer=out_br_patch_name)

                if not access_br.port_exist(port_name=remote_port_name):
                    access_br.add_port(remote_port_name, port_type=data.VXLAN, vxlan_remote_ip=agent_ip, vxlan_key=vxlan_key)

        self.out_br.add_port(out_br_patch_name, vlan_vid=vlan_id, port_type=data.PATCH, patch_peer=patch_port_name)


class AgentConfig(object):
    def __init__(self, agent_ip, agent_port=data.OVS.MANAGERPORT):
        self.agent_ip = agent_ip
        self.agent_port = agent_port
        self.ovs_manager = ovs_manager

        ovs_manager.add_container(agent_ip, agent_port)

    def access_port(self, access_br=None, entity_gate=None, access_port=None, vxlan_key=None):
        container = self.ovs_manager.get_container(self.agent_ip)
        access_br = str(access_br)
        if access_br:
            access_datapath = container.get_br(access_br)
            if not access_datapath:
                access_datapath = container.add_br(access_br)

        access_datapath.add_port(access_port, port_type=data.VXLAN, vxlan_remote_ip=entity_gate, vxlan_key=vxlan_key)












