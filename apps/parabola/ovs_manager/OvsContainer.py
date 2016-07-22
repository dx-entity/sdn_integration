from OvsVsctl import get_ctl
from OvsVsctl import _db_find
import apps.parabola.static as data


class ContainerRegister(object):

    _instance = None

    def __init__(self):
        super(ContainerRegister,self).__init__()
        self.container_list = {}

    def regist_container(self, container_list):
        ret = []
        for con in container_list:
            c = Container(con[0], con[1])
            self.container_list[con[0]] = c
            ret.append(c)
        return ret

    def get_container(self, con_ip):
        return self.container_list[con_ip] if self.container_list.has_key(con_ip) else None


class Container(object):

    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.br_list = {}

        self.init_get_br()

    def init_get_br(self):
        ovs = get_ctl()
        br = ovs.list_br(self.ip, self.port).execute()
        for b in br:
            if not self.br_exist(b):
                self.br_list[b] = OvsBr(b, self)

    def get_br(self, br_name):
        return self.br_list[br_name] if self.br_exist(br_name) else None

    def get_all(self):
        return self.br_list

    def br_exist(self, br_name):
        return br_name in self.br_list

    def add_br(self, br_name):
        '''
        do
        ovs-vsctl add-br [br-name]
        :return:
        '''
        if self.br_exist(br_name):
            raise NameError
        ovs = get_ctl()
        try:
            ovs.add_br(br_name, remote_ovs=self.ip, remote_port=self.port).execute()
        except Exception as e:
            print 'add_br failed'
        br = OvsBr(br_name,self)
        self.br_list[br_name] = br
        return br

    def del_br(self, br_name):
        '''
        do
        ovs-vsctl del-br [br-name]
        :return:
        '''
        self.init_get_br()
        if not self.br_exist(br_name):
            raise NameError
        ovs = get_ctl()
        try:
            ovs.del_br(br_name, remote_ovs=self.ip, remote_port=self.port).execute()
        except Exception as e:
            print 'del_br failed'
        self.br_list.pop(br_name)
        return

    def __str__(self, level=0):
        ret = '\t'*level + ':'.join([self.ip, self.port]) + '\n'
        for br_name in self.br_list:
            ret += self.br_list[br_name].__str__()


        return ret

class OvsBr(object):

    def __init__(self, br_name, container):
        super(OvsBr, self).__init__()
        self.container = container
        self.br_name = br_name
        self.port_list = {}

        self.bridge_init()
        self.init_get_port()

    def __str__(self, level=1):
        ret = '\t'*level+'br_name:'+self.br_name+'\n'
        for port_name in self.port_list:
            ret += self.port_list[port_name].__str__()
        return ret

    def bridge_init(self):
        self.static = _db_find('bridge', ['name', self.br_name], remote_ovs=self.container.ip, remote_port=self.container.port)

    def port_exist(self, port_name):
        return port_name in self.port_list


    def init_get_port(self):
        ovs = get_ctl()
        port_list = ovs.list_ports(self.br_name, remote_ovs=self.container.ip, remote_port=self.container.port).execute()
        for port in port_list:
            if port not in self.port_list:
                self.port_list[port] = OvsPort(port, self)

    def get_port(self, port_name):
        return self.port_list[port_name] if port_name in self.port_list else None

    def del_port(self, port_name):
        '''
        do
        ovs-vsctl del-port [portname]
        :return:
        '''
        self.init_get_port()
        if port_name not in self.port_list:
            raise NameError
        ovs = get_ctl()
        try:
            ovs.del_port(port_name, remote_ovs=self.container.ip, remote_port=self.container.port).execute()
        except Exception as e:
            print 'del_port failed'
        # print self.port_list
        self.port_list.pop(port_name)
        # print self.port_list


    def add_port(self, port_name, port_type=data.INTERNAL, patch_peer=None, vxlan_remote_ip=None, vxlan_key=None, vlan_vid=None , trunk_permit=None):
        if port_name in self.port_list:
            raise NameError
        ovs = get_ctl()
        try:
            ovs.add_port(self.br_name, port_name,\
                         port_type=port_type, patch_peer=patch_peer,\
                         vxlan_remote_ip=vxlan_remote_ip, vxlan_key=vxlan_key,\
                         vlan_vid=vlan_vid, trunk_permit=trunk_permit,\
                         remote_ovs=self.container.ip, remote_port=self.container.port).execute()
        except Exception as e:
            print e
            print 'add_port failed'

        port = OvsPort(port_name, self, port_type=port_type, patch_peer=patch_peer,\
                         vxlan_remote_ip=vxlan_remote_ip, vxlan_key=vxlan_key,\
                         vlan_vid=vlan_vid, trunk_permit=trunk_permit)
        self.port_list[port_name] = port
        return port

    def set_port(self, port_name, port_type=data.INTERNAL, vlan_vid=None , trunk_permit=None):
        if not port_name in self.port_list:
            raise NameError
        ovs = get_ctl()

        try:
            ovs.set(port_name, set_type='port',\
                         port_type=port_type,\
                         vlan_vid=vlan_vid, trunk_permit=trunk_permit,\
                         remote_ovs=self.container.ip, remote_port=self.container.port).execute()
        except Exception as e:
            print e
            print 'set_port failed'
        port = OvsPort(port_name, self, port_type=port_type, patch_peer=None,\
                         vxlan_remote_ip=None, vxlan_key=None,\
                         vlan_vid=vlan_vid, trunk_permit=trunk_permit)

        self.port_list[port_name] = port
        return port


    def flow_action(self):

        pass


class OvsPort(object):
    def __init__(self, *args, **kwargs):
        super(OvsPort, self).__init__()
        self.port_name = args[0]
        self.br = args[1]
        self.basic_info = kwargs
        self.interface_list = {self.port_name: OVSInterface(self)}
        self.port_init()

    def __str__(self, level=2):
        ret = '\t'*level + 'port_name:' + self.port_name + '\n'
        ret += '\t'*level + 'port_tag:' + str(self.tag) + '\n'
        ret += '\t'*level + 'trunk:' + str(self.trunk) + '\n'
        ret += '\t'*level + 'vlan_mode:' + str(self.vlan_mode) + '\n'

        for interface in self.interface_list:
            ret += self.interface_list[interface].__str__()
        return ret

    def port_init(self):
        self.static = _db_find('port', ['name', self.port_name], remote_ovs=self.br.container.ip, remote_port=self.br.container.port)[0]
        self.tag = self.static['tag']
        self.trunk = self.static['trunks']
        self.vlan_mode = self.static['vlan_mode']

    def get_interface(self, inter_name):
        return self.interface_list.get(inter_name, None)

    def set_interface(self, inter_name, port_type=data.INTERNAL, patch_peer=None, vxlan_remote_ip=None, vxlan_key=None):
        if not inter_name in self.interface_list:
            raise NameError
        ovs = get_ctl()

        try:
            ovs.set(inter_name, set_type='interface', port_type=port_type,\
                         patch_peer=patch_peer, vxlan_remote_ip=vxlan_remote_ip, vxlan_key=vxlan_key,\
                         remote_ovs=self.br.container.ip, remote_port=self.br.container.port).execute()
        except Exception as e:
            print e
            print 'set_port failed'
        interface = OVSInterface(self)

        self.interface_list[inter_name] = interface
        return interface

    def get_port_status(self):
        pass

    def get_port_details(self):
        pass


class OVSInterface(object):
    def __init__(self, port):
        super(OVSInterface, self).__init__()
        self.port = port
        self.interface_name = port.port_name
        self.interface_init()

    def __str__(self, level=3):
        ret = '\t'*level+'interface_name:'+self.interface_name+'\n'
        ret += '\t'*level + 'interface_type:'+self.static['type'] + '\n'
        ret += '\t'*level + 'cur_state:'+self.static['link_state'] + '\n'
        ret += '\t'*level + 'mac:'+self.static['mac_in_use'] + '\n'
        return ret


    def interface_init(self):

        self.static = _db_find('interface', ['name', self.interface_name], remote_ovs=self.port.br.container.ip, remote_port=self.port.br.container.port)[0]
        # print self.static

    def get_interface_details(self):
        pass

