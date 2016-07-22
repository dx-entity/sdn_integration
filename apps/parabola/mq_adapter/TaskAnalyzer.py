from abc import ABCMeta, abstractmethod
from apps.parabola.calculate.XMLAnalyser import XMLAnalyser
from apps.parabola.calculate.EntityAccessPortAllocate import EntityAccessPortAllocate
from apps.parabola.calculate.ContainerGenerate import ContainerGenerater
from apps.parabola.mq_adapter.ResultSender import ResultSender
from apps.parabola.mq_adapter.MsgTemplate import TaskMsgGenerator
from apps.parabola.mq_adapter.MsgTemplate import HeartBeatMsgGenerator
import apps.parabola.static as data
from apps.parabola.ovs_manager.OvsManager import OvsManager
from apps.parabola.ovs_manager.OvsAdapter import OvsAdapter
from apps.parabola.LogFormater import get_logger
from apps.parabola.global_view.global_statics import GlobalCaseInfo


class BaseTaskAnalyser(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def analyse_task(self):
        pass

    @abstractmethod
    def do_task(self):
        pass


class DeployTaskAnalyser(BaseTaskAnalyser):
    def __init__(self, msg):
        self.msg = msg
        self.LOGGER = get_logger(self.__class__.__name__)

    def analyse_task(self, container_list, mapping):
        """
        map the node_id to vxlan_id
        according to real_node_id and link_node_id is equal
        :param container_list:
        :param mapping:
        :return: res_dict: [{"vlan_id":"***","vxlan_id": "****", "br_name":"br0", "container_ip":"****"}]
        """
        res_dict = []
        container_set = []

        for link in mapping:
            tmp = {"vxlan_id": "****", "agent_br_name": "br0", "container_ip": "****", "vlan_id": "**"}
            for container in container_list:
                if link['node_id'] in container["node_list"]:
                    tmp["vxlan_id"] = link["vxlan_id"]
                    tmp["agent_br_name"] = container["ovs_br"]
                    tmp["access_br_name"] = link["br_name"]
                    tmp["container_ip"] = container["container_ip"]
                    tmp["vlan_id"] = link["vlan_id"]
                    tmp["node_id"] = link["node_id"]
                    res_dict.append(tmp)
                container_set.append(container["container_ip"])

        return res_dict, list(set(container_set))

    def do_task(self):
        """
        main func to handle deploy task:
        1. analyse xml get link relations;
        2. allocate access switch port;
        3. get the container's IP and init container;
        4. modify ovs configuration;
        5. return task msg;
        :return:
        """
        msg_type = self.msg[data.MSG.TASKTYPE]
        if msg_type != data.MSG.TASKTODO:
            return
        result_sender = ResultSender.get_instance()

        case_id = self.msg[data.MSG.CASEID]
        xml_file_path = ''.join([data.NFS.NFSBASE, self.msg[data.MSG.DEFINE][data.MSG.TFILE]])
        self.LOGGER.info('case_id is ' + case_id + '\t' * 2 + xml_file_path)

        gci = GlobalCaseInfo.get_instance()

        # analyse xml and get the real node link relations
        xml_analyser = XMLAnalyser(xml_file_path)
        link_relation = xml_analyser.xml_analyser()

        try:
            if len(link_relation) > len(gci.update_access_port()):
                gci.refresh_access_port()
                if len(link_relation) > len(gci.update_access_port()):
                    # TODO raise an exception that resource not enough
                    raise OverflowError("resource not enough")
        except OverflowError, e:
            self.LOGGER.exception(e)

        self.LOGGER.info('analyse xml success')
        # get access agent configuration
        pa = EntityAccessPortAllocate(case_id)
        res, mapping, name = pa.allocate_port(link_relation)

        self.LOGGER.info('access switch init ok')
        if not res:
            return

        # get other agent ip and manage object
        cg = ContainerGenerater(case_id, link_relation)
        container_list = cg.get_container_ip()

        res_dic, container_set = self.analyse_task(container_list, mapping)
        container_port = []
        for container in container_set:
            container_port.append(data.OVS.MANAGERPORT)

        # init agent container
        ovs_manager = OvsManager.get_instance()
        container_obj = ovs_manager.add_container(container_set, container_port)
        self.LOGGER.info("container init --- ok ")

        # register in global data statics

        gci.regist_info_structure(case_id=case_id, container_list=container_obj, entity_entry=gci.get_entity_entry(),
                                  ovs_configure=res_dic)

        oa = OvsAdapter()

        # TODO: res
        try:
            oa.handle_case_task(case_id=case_id)
        except Exception, e:
            self.LOGGER.exception(e)
            # TODO : return task failed msg
            send_msg = TaskMsgGenerator(self.msg[data.MSG.CASEID], self.msg[data.MSG.TASKID], data.MSG.TASKBACK,
                                        self.msg[data.MSG.SERVERIP], self.msg[data.MSG.TASKNAME]).get_msg()
            result_sender.send_msg(send_msg)

        send_msg = TaskMsgGenerator(self.msg[data.MSG.CASEID], self.msg[data.MSG.TASKID], data.MSG.TASKBACK,
                                    self.msg[data.MSG.SERVERIP], self.msg[data.MSG.TASKNAME]).get_msg()

        self.LOGGER.info(send_msg)

        result_sender.send_msg(send_msg)


class CloseTaskAnalyser(BaseTaskAnalyser):
    def __init__(self, msg):
        self.msg = msg
        self.LOGGER = get_logger(self.__class__.__name__)
        self.result_sender = ResultSender.get_instance()

    def analyse_task(self, case_id):
        gci = GlobalCaseInfo.get_instance()
        """
        TODO: result conllection
        """

        try:
            gci.clean_case(case_id)
        except Exception, e:
            self.LOGGER.exception(e)
            send_msg = TaskMsgGenerator(self.msg[data.MSG.CASEID], self.msg[data.MSG.TASKID], data.MSG.TASKBACK,
                                        self.msg[data.MSG.SERVERIP], self.msg[data.MSG.TASKNAME]).get_msg()
            self.result_sender.send_msg(send_msg)

        send_msg = TaskMsgGenerator(self.msg[data.MSG.CASEID], self.msg[data.MSG.TASKID], data.MSG.TASKBACK,
                                    self.msg[data.MSG.SERVERIP], self.msg[data.MSG.TASKNAME]).get_msg()

        self.result_sender.send_msg(send_msg)

    def do_task(self):
        msg_type = self.msg[data.MSG.TASKTYPE]
        if msg_type != data.MSG.TASKTODO:
            return

        self.analyse_task(self.msg[data.MSG.CASEID])


class OrdinarilyAnalyser(BaseTaskAnalyser):
    def __init__(self, msg):
        self.msg = msg

    def analyse_task(self):
        pass

    def do_task(self):
        temp_res = {data.MSG.RES.CONCLUSION: 1, data.MSG.RES.DESCRIPTION: "", data.MSG.RES.DONE: 1, data.MSG.RES.NEED: 1}
        send_msg = TaskMsgGenerator(self.msg[data.MSG.CASEID], self.msg[data.MSG.TASKID], data.MSG.TASKBACK,
                                    self.msg[data.MSG.SERVERIP], self.msg[data.MSG.TASKNAME], res=temp_res).get_msg()
        result_sender = ResultSender.get_instance()
        result_sender.send_msg(send_msg)


class HeartbeatAnalyser(BaseTaskAnalyser):
    def __init__(self, msg):
        self.msg = msg
        self.LOGGER = get_logger(self.__class__.__name__)

    def analyse_task(self):
        pass

    def do_task(self):
        ip = self.msg[data.MSG.IPADDR]
        if ip == get_ip(network_card="enp0s25"):
            msg = HeartBeatMsgGenerator(self.msg[data.MSG.ID], ip, self.msg[data.MSG.TASKNAME], data.MSG.MODULENAME).get_msg()
            result_sender = ResultSender.get_instance()
            result_sender.send_msg(msg, task=False)


def get_ip(network_card='eth0'):
    import socket
    import fcntl
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', network_card[:15])
    )[20:24])
