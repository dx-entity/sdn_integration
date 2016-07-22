from apps.parabola import static as data
from apps.parabola.ovs_manager.OvsManager import OvsManager
from apps.parabola.dao.DBConnector import DBConnector
from apps.parabola.dao.close_clean_data import clean_data
from apps.parabola.LogFormater import get_logger

_ovs_manager = OvsManager.get_instance()


def get_global():
    container_list = _ovs_manager.get_all()
    for con_ip in container_list:
        print container_list[con_ip]


def refresh_data():
    # TODO: refresh b_access_switch. remove the close case data
    db = DBConnector()
    sql = "select case_id, state from b_case where case_id in (select case_id from b_access_switch where case_id!='')"

    res = db.do_query(sql)
    case_to_clean = []
    for r in res:
        case_state = r[1]
        case_id = r[0]
        if case_state in [data.CASESTATE.CASEDEFINED, data.CASESTATE.CASECLOSED]:
            case_to_clean.append(case_id)

    for caseid in case_to_clean:
        sql = "update b_access_switch set case_id='' where case_id='{0}'".format(caseid)
        db.update_all(sql)


def get_access_port():
    db = DBConnector()
    sql_port = "select * from b_access_switch where case_id='';"

    res = db.do_query(sql=sql_port)

    gci = GlobalCaseInfo.get_instance()
    temp = list()

    print res

    for port in res:
        tmp = dict()
        tmp['switch_id'] = int(port[0])
        tmp['port_id'] = int(port[1])
        tmp['vlan_id'] = int(port[4])
        temp.append(tmp)

    gci.access_port_pool.extend(temp)


class GlobalCaseInfo(object):

    _global_case_info = None

    def __init__(self):
        self.global_case_info_structure = {}
        self.entity_entry_pool = {}
        self.access_port_pool = []

    @staticmethod
    def get_instance():
        if not GlobalCaseInfo._global_case_info:
            GlobalCaseInfo._global_case_info = GlobalCaseInfo()
        return GlobalCaseInfo._global_case_info

    def add_entity_entry(self, ip, en):
        if not self.entity_entry_pool.get(ip, None):
            self.entity_entry_pool[ip] = en

    def get_entity_entry(self, ip=None):
        if not ip:
            keys = self.entity_entry_pool.keys()
            if keys:
                return self.entity_entry_pool[keys[0]]
            return None
        return self.entity_entry_pool.get(ip, None)

    def regist_info_structure(self, case_id, container_list=None, entity_entry=None, ovs_configure=None):
        self.global_case_info_structure[case_id] = CaseInfo(case_id, container_list, entity_entry, ovs_configure)

    def get_info_structure(self, case_id):
        return self.global_case_info_structure.get(case_id, None)

    def clean_case(self, case_id):
        case_info = self.global_case_info_structure.get(case_id, None)
        if not case_info:
            raise KeyError("no such case in restore")
        case_info.clean_self()
        del self.global_case_info_structure[case_id]

        return
    #     case_detail = self.global_case_info_structure.get(case_id, None)
    #     if not case_detail:
    #         return None
    #
    #     pre_clean = case_detail.get_detail()
    #     for container in pre_clean:
    #         con = _ovs_manager.get_container(container.ip)
    #         for br in pre_clean[container]:
    #             con.del_br(br.br_name)

    def update_access_port(self):
        self.access_port_pool = []
        get_access_port()
        return self.access_port_pool

    def refresh_access_port(self):
        refresh_data()

# all the dict info is stored in [container object]: [br object]


class CaseInfo(object):

    def __init__(self, case_id, container_dict, entity_entry, ovs_configure):
        self.case_id = case_id
        self.container_dict = container_dict
        self.entity_entry = entity_entry
        self.ovs_configure = ovs_configure
        self.LOG = get_logger(__name__)

    def set_case(self, container_dict):
        self.container_dict = container_dict

    def get_detail(self):
        return self.container_dict

    def clean_self(self):
        try:
            for ovs_br in self.ovs_configure:
                access_container = _ovs_manager.get_container(self.entity_entry.entity_gate)

                if not access_container.br_exist(ovs_br['access_br_name']) or not access_container:
                    raise NameError
                access_container.del_br(str(ovs_br['access_br_name']))
                base_br = access_container.get_br('br_base')

                base_br.del_port(''.join(['patch_', ovs_br['access_br_name'], '_master']))

                container = _ovs_manager.get_container(ovs_br['container_ip'])
                if not container.br_exist(ovs_br['agent_br_name']) or not container:
                    raise NameError
                container.del_br(str(ovs_br['agent_br_name']))
        except Exception, e:
            self.LOG.exception(e)

        self.LOG.info("case {0} clean ovs ok".format(self.case_id))

        clean_data(self.case_id)

        self.LOG.info("case {0} clean database ok".format(self.case_id))

        return True