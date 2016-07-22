from OvsContainer import ContainerRegister
# import logging


class OvsManager(object):

    _ovs_container_register = ContainerRegister()

    _ovs_manager = None

    def __init__(self):
        super(OvsManager, self).__init__()

    @staticmethod
    def get_instance():
        if not OvsManager._ovs_manager:
            OvsManager._ovs_manager = OvsManager()
        return OvsManager._ovs_manager

    def add_container(self, con_ip, con_port):
        ip = []
        port = []
        ip.extend(con_ip) if isinstance(con_ip, list) else ip.append(con_ip)
        port.extend(con_port) if isinstance(con_port, list) else port.append(con_port)
        if len(ip) != len(port):
            raise NameError
        return self._ovs_container_register.regist_container(map(lambda x,y: [x,y], ip, port))

    def get_container(self, con_ip):
        return self._ovs_container_register.get_container(con_ip)

    def get_all(self):
        return self._ovs_container_register.container_list


