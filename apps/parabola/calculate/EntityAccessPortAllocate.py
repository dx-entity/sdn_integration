
from apps.parabola.dao.DBConnector import DBConnector
from apps.parabola.config_init import *


class EntityAccessPortAllocate(object):
    def __init__(self, caseid):
        self.caseid = caseid

    def get_access_port_info(self, link_relation):
        """
        get port according to link num;
        related data comes from data base;
        port_info num is link num;
        node_id is real node_id;
        :param link_num: the num need to allocate to each link
        :return: port_info: dict, [{"port_name":"***", "vlan_id":"***", "vxlan_id":"***", "node_id":"****"}, ....]
        """
        link_num = 0
        for node in link_relation:
            link_num += len(node['node_link'])

        dbconn = DBConnector()

        sql_get_case_port = "select switch_id, port_id, vlan_id from b_access_switch where case_id='{0}'".format(self.caseid)
        res = dbconn.do_query(sql_get_case_port)

        if not res:
            sql_get_port = "select switch_id, port_id, vlan_id from b_access_switch where case_id='' limit {0}".format(str(link_num))
            res = dbconn.do_query(sql_get_port)

        if len(res) < link_num:
            # TODO raise an exception, no enough resource
            pass

        port_info = list()

        port_list = list(res)
        for link in link_relation:
            port = port_list.pop(0)
            vlan_id = str(port[2])
            tmp_port_info = dict()
            tmp_port_info['br_name'] = "br"+vlan_id
            tmp_port_info['port_name'] = "port"+vlan_id
            tmp_port_info['vlan_id'] = vlan_id
            tmp_port_info['vxlan_id'] = vlan_id
            tmp_port_info['node_id'] = link['node_id']
            port_info.append(tmp_port_info)

        # port_info = [{"br_name":"br0","port_name": "port1", "vlan_id": "200", "vxlan_id": "120", "node_id": "404142"}]
        return port_info

    def allocate_port(self, link_relation):
        """
        according to the link_num  allocate the access port and update database
        :param link_relation: real node link relation
        :return: res: bool, allocate result
                mapping: dict, return node map to the access port
                name: str, reason why allocate failed, if allocate success then None
        """
        res = True
        name = None
        mapping = None

        mapping = self.get_access_port_info(link_relation)

        return res, mapping, name
