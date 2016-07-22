import DBConnector


def update_success(case_id, vlan_id, node_id, ovs_name, server_ip, container_type):
    sql_insert_ovs = '''
        insert into b_case_ovs (caseid, server_ip, ovs_name, occupy_vlanid, container_type)
        VALUE ('{0}','{1}','{2}','{3}','{4}')
    '''.format(case_id, server_ip, ovs_name, vlan_id, container_type)

    sql_update_access = '''
        update b_access_switch set case_id='{0}', node_id='{1}' where vlan_id='{2}'
    '''.format(case_id, node_id, vlan_id)

    db = DBConnector.DBConnector()

    db.insert_one(sql_insert_ovs)
    db.update_all(sql_update_access)