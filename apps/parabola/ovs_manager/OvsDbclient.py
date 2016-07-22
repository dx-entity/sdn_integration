# ---------------------------------
# TODO: finish this ovsdb client
# ---------------------------------

import os
from ovs import jsonrpc, stream
from ovs import util as ovs_util


class OvsDBclient(object):
    def __init__(self, ovs_db_ip, ovs_port='6640', proto='tcp'):
        super(OvsDBclient, self).__init__()
        self.ovs_db_ip = ovs_db_ip
        self.ovs_port = ovs_port
        self.proto = proto

    def _get_connection(self):
        error, stream_ = stream.Stream.open_block(
            stream.Stream.open(':'.join([self.proto, self.ovs_db_ip, self.ovs_port])))
        if error:
            raise RuntimeError('can not open socket to %s: %s' %
                               (self.ovs_db_ip, os.strerror(error)))

        rpc = jsonrpc.Connection(stream_)

        request = jsonrpc.Message.create_request('list_dbs', [])
        error, reply = rpc.transact_block(request)

        if error:
            ovs_util.ovs_fatal(error, os.strerror(error))
        elif reply.error:
            ovs_util.ovs_fatal(reply.error, 'error %s' % reply.error)

    def set_interface_vxlan(self, port_name, remote_ip):
        pass
