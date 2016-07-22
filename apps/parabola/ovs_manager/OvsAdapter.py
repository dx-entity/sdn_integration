from apps.parabola.dao import update_success_data
import apps.parabola.static as data

from apps.parabola.global_view.global_statics import GlobalCaseInfo
from apps.parabola.entity_access.EntityAccess import AgentConfig

class OvsAdapter(object):

    def __init__(self):
        self.gci = GlobalCaseInfo.get_instance()

    def handle_case_task(self, case_id):
        self.case_id = case_id
        case_info = self.gci.get_info_structure(case_id)
        ovs_configure = case_info.ovs_configure
        entity_access = case_info.entity_entry
        print ovs_configure
        for task in ovs_configure:
            self.do_ovs_task(task, entity_access)

    def do_ovs_task(self, task, entity_access):

        vxlan_id = task["vxlan_id"]
        agent_br_name = task["agent_br_name"]
        vlan_id = task["vlan_id"]
        node_id = task["node_id"]
        access_br_name = task["access_br_name"]
        patch_port_name = 'patch_'+access_br_name
        remote_port_name = 'vxlan_'+access_br_name

        entity_access.add_agent_access_br(br_name=access_br_name, patch_port_name=patch_port_name, vlan_id=vlan_id, remote_port_name=remote_port_name, vxlan_key=vxlan_id, agent_ip=task["container_ip"])
        update_success_data.update_success(self.case_id, vlan_id, node_id, access_br_name, entity_access.entity_gate, data.OVS.OVSType.ACCESS)

        agent = AgentConfig(agent_ip=task["container_ip"])
        agent.access_port(access_br=agent_br_name, entity_gate=entity_access.entity_gate, access_port=remote_port_name, vxlan_key=vxlan_id)
        update_success_data.update_success(self.case_id, vlan_id, node_id, agent_br_name, task["container_ip"], data.OVS.OVSType.AGENT)

    def name_gen(self, br, agent):
        """
        get a name, must not return a same name on same container
        :param br: indicate name a br/port;
        :param agent: indicate name a agent/access;
        :return: name: a name
        """
        name = None
        return name

