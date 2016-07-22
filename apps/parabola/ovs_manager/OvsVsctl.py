import itertools

from neutron.agent.ovsdb.impl_vsctl import OvsdbVsctl
from neutron.agent.ovsdb.impl_vsctl import BaseCommand
from neutron.agent.ovsdb.impl_vsctl import Transaction
from neutron.agent.ovsdb.impl_vsctl import MultiLineCommand
from neutron.agent.ovsdb.impl_vsctl import DbCommand

import apps.parabola.static as data


class Context(object):
    def __init__(self):
        pass

context = Context()

context.vsctl_timeout = 10


class CustomCommand(BaseCommand):

    def __init__(self, context, cmd, opts=None, args=None, tr_opt=None):
        super(CustomCommand, self).__init__(context, cmd, opts=opts, args=args)
        self.tr_opt = tr_opt

    def execute(self, check_error=False, log_errors=True):
        with Transaction(self.context, check_error=check_error,
                         log_errors=log_errors, opts=self.tr_opt) as txn:
            txn.add(self)
        return self.result


class CustomMultilineCommand(MultiLineCommand):
    def __init__(self, context, cmd, opts=None, args=None, tr_opt=None):
        super(CustomMultilineCommand, self).__init__(context, cmd, opts=opts, args=args)
        self.tr_opt = tr_opt

    def execute(self, check_error=False, log_errors=True):
        with Transaction(self.context, check_error=check_error,
                         log_errors=log_errors, opts=self.tr_opt) as txn:
            txn.add(self)
        return self.result


class CustomDBCommand(DbCommand):
    def __init__(self, context, cmd, opts=None, args=None, tr_opt=None, columns=None):
        super(CustomDBCommand, self).__init__(context, cmd, opts=opts, args=args, columns=columns)
        self.tr_opt = tr_opt

    def execute(self, check_error=False, log_errors=True):
        with Transaction(self.context, check_error=check_error,
                         log_errors=log_errors, opts=self.tr_opt) as txn:
            txn.add(self)
        return self.result


class CustomOVS(OvsdbVsctl):
    def add_port(self, bridge, port, port_type=data.INTERNAL, may_exist=True, patch_peer=None, vxlan_remote_ip=None, vxlan_key=None, vlan_vid=None, trunk_permit=None,remote_ovs=None, remote_port=None):
        opts = []
        param = [bridge, port]
        tr_opt = []
        tr_opt.extend( ['--db=tcp:{0}'.format((':'.join([remote_ovs,remote_port])))] ) if remote_ovs and remote_port else None
        opts.extend(['--may-exist']) if may_exist else []
        param.extend(['tag={0}'.format(vlan_vid)]) if vlan_vid else None
        param.extend(['--','set','interface',port, 'type={0}'.format(port_type),'option:remote_ip={0}'.format(vxlan_remote_ip)]) if port_type==data.VXLAN else None
        param.extend(['option:key={0}'.format(vxlan_key)]) if vxlan_key and port_type==data.VXLAN else None
        param.extend(['--','set','interface',port, 'type={0}'.format(port_type)]) if port_type==data.INTERNAL else None
        param.extend(['--','set','interface',port, 'type={0}'.format(port_type),'option:peer={0}'.format(patch_peer)]) if port_type==data.PATCH else None
        param.extend(['--','set','port',port, 'vlan_mode={0}'.format(port_type), 'trunks={0}'.format(str(trunk_permit))]) if port_type==data.TRUNK else None

        return CustomCommand(self.context, 'add-port', opts, param, tr_opt=tr_opt)

    def list_br(self, remote_ovs=None, remote_port=None):
        tr_opt=[]
        tr_opt.extend( ['--db=tcp:{0}'.format((':'.join([remote_ovs,remote_port])))] ) if remote_ovs and remote_port else None

        return CustomMultilineCommand(self.context, 'list-br', tr_opt=tr_opt)

    def add_br(self, name, remote_ovs=None, remote_port=None):
        tr_opt=[]
        tr_opt.extend( ['--db=tcp:{0}'.format((':'.join([remote_ovs,remote_port])))] ) if remote_ovs and remote_port else None

        args = []
        args.append(name) if isinstance(name, str) else args.extend(name)

        return CustomCommand(self.context, 'add-br', args=args, tr_opt=tr_opt)

    def del_br(self, name, remote_ovs=None, remote_port=None, if_exists=True):
        tr_opt = []
        tr_opt.extend(
            ['--db=tcp:{0}'.format((':'.join([remote_ovs, remote_port])))]) if remote_ovs and remote_port else None

        args = []
        args.append(name) if isinstance(name, str) else args.extend(name)


        return CustomCommand(self.context, 'del-br', tr_opt=tr_opt, args=args)


    def list_ports(self, br_name, remote_ovs=None, remote_port=None ):
        tr_opt = []
        tr_opt.extend(
            ['--db=tcp:{0}'.format((':'.join([remote_ovs, remote_port])))]) if remote_ovs and remote_port else None

        args = []
        args.append(br_name) if isinstance(br_name, str) else args.extend(br_name)

        return CustomMultilineCommand(self.context, 'list-ports', tr_opt=tr_opt, args=args)

    def del_port(self, port_name, remote_ovs=None, remote_port=None):
        tr_opt = []
        tr_opt.extend(
            ['--db=tcp:{0}'.format((':'.join([remote_ovs, remote_port])))]) if remote_ovs and remote_port else None

        args = []
        args.append(port_name) if isinstance(port_name, str) else args.extend(port_name)

        return CustomCommand(self.context, 'del-port', tr_opt=tr_opt, args=args)

    def set(self, name, set_type=None, port_type=data.INTERNAL, may_exist=False, vlan_vid=None, trunk_permit=None, patch_peer=None, vxlan_remote_ip=None, vxlan_key=None, remote_ovs=None, remote_port=None):
        opts = []
        if not set_type:
            print 'indecate set type'
        param = [set_type, name]
        tr_opt = []
        tr_opt.extend(
            ['--db=tcp:{0}'.format((':'.join([remote_ovs, remote_port])))]) if remote_ovs and remote_port else None
        opts.extend(['--may-exist']) if may_exist else []
        param.extend(['tag={0}'.format(vlan_vid)]) if vlan_vid else None

        param.extend(['vlan_mode={0}'.format(port_type),
                      'trunks={0}'.format(str(trunk_permit))]) if port_type == data.TRUNK else None
        param.extend(['type={0}'.format(port_type), 'option:peer={0}'.format(patch_peer)]) if port_type==data.PATCH else None

        param.extend(['type={0}'.format(port_type), 'option:remote_ip={0}'.format(vxlan_remote_ip)]) if port_type==data.VXLAN else None

        param.extend(['option:key={0}'.format(vxlan_key)]) if port_type==data.VXLAN and vxlan_key != None else None

        return CustomCommand(self.context, 'set', opts, param, tr_opt=tr_opt)

    def flow_actions(self, name, action, *args, **kwargs):
        if action not in ['del', 'add', 'mod']:
            raise NameError

        cmd = ['ovs-ofctl', action+'-flow', name]



        return


def _db_find(table, *conditions, **kwargs):
    tr_opt = []
    remote_ovs=kwargs.get('remote_ovs',None)
    remote_port=kwargs.get('remote_port',None)
    tr_opt.extend(
        ['--db=tcp:{0}'.format( (':'.join([remote_ovs, remote_port])) )]) if remote_ovs and remote_port else None

    from neutron.agent.ovsdb.impl_vsctl import _set_colval_args
    columns = kwargs.pop('columns', None)
    args = itertools.chain([table],
                           *[_set_colval_args(c) for c in conditions])

    return CustomDBCommand(context, 'find', args=args, columns=columns, tr_opt=tr_opt).execute()


def get_ctl():
    return CustomOVS(context)