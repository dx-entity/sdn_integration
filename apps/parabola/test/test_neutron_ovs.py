from neutron.agent.ovsdb.impl_vsctl import OvsdbVsctl
from neutron.agent.ovsdb.impl_vsctl import BaseCommand
from neutron.agent.ovsdb.impl_vsctl import Transaction

class Context(object):
    def __init__(self):
        pass

context = Context()

context.vsctl_timeout=5

class CustomCommand(BaseCommand):

    def __init__(self, context, cmd, opts=None, args=None, tr_opt=None):
        super(CustomCommand, self).__init__(context, cmd, opts=opts, args=args)
        self.tr_opt = tr_opt

    def execute(self, check_error=False, log_errors=True):
        with Transaction(self.context, check_error=check_error,
                         log_errors=log_errors, opts=self.tr_opt) as txn:
            txn.add(self)
        return self.result


class CustomOVS(OvsdbVsctl):
    def add_port(self, bridge, port, may_exist=True, remote_ip=None, vlan_vid=None, remote_ovs=None, remote_port=None):
        opts = []
        param = [bridge, port]
        tr_opt = []
        tr_opt.extend( [ '--db=tcp:{0}'.format( (':'.join( [remote_ovs,remote_port] ) ) ) ] )
        opts.extend(['--may-exist']) if may_exist else []
        param.extend(['tag={0}'.format(vlan_vid)]) if vlan_vid else None
        param.extend(['--','set','interface',port, 'type=vxlan','option:remote_ip={0}'.format(remote_ip)]) if remote_ip else \
            param.extend(['--','set','interface',port, 'type=internal'])

        return CustomCommand(self.context, 'add-port', opts, param, tr_opt=tr_opt)

# print context.vsctl_timeout

ovs = CustomOVS(context)

# print ovs.add_port('br0', 'tp1', remote_ip='10.0.0.1', vlan_vid='100',remote_ovs='192.168.252.160',remote_port='6640').execute()

print ovs.list_ports('br0').execute()
# print ovs.list_br().execute()
# print ovs.add_br('testbr1').execute()
# print ovs.add_port('testbr1', 'tp').execute()
# print ovs.list_ports('testbr1').execute()
