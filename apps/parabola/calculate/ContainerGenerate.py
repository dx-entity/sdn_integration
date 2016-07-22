from apps.parabola.dao.DBConnector import DBConnector
from apps.parabola.ovs_manager.OvsContainer import Container


class ContainerGenerater(object):
    def __init__(self, case_id, link_relation):
        self.case_id = case_id
        self.link_relation = link_relation
        self.db = DBConnector()

    def get_container_ip(self):
        """
        get container ip according to case_id;
        generate a dict like [{"container_ip":"172.16.21.22", "ovs_br":["br0","br1"]},....]
        :return: container_list
        """

        sql_container = "select * from b_entity_access where case_id={0}".format(self.case_id)

        res = self.db.do_query(sql=sql_container)

        container_list = []

        entity_node_id = set([link['node_id'] for link in self.link_relation])

        for container in res:
            tmp = {}
            node_list = set(container[4].split(','))
            if node_list & entity_node_id:
                tmp['container_ip'] = container[2]
                tmp['ovs_br'] = container[1]
                tmp['node_list'] = container[4].split(',')
                container_list.append(tmp)
        return container_list
