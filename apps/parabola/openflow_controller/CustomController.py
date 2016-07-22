import logging
import json
import sys

from webob import Response

from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import WSGIApplication
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import dpset
from ryu.controller import handler
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import HANDSHAKE_DISPATCHER
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
from ryu.lib import ofctl_v1_3
from ryu.lib.packet import vlan as vlan_header
from ryu.lib import dpid as dpid_lib
from ryu.ofproto import ether
from ryu.ofproto import inet
from ryu import utils
from entity_model.CustomSwitch import *

REST_SWITCHID = 'switch_id'
REST_ALL = 'all'
REST_STATUS_ENABLE = 'enable'
REST_STATUS_DISABLE = 'disable'
REST_STATUS = 'status'

STATUS_FLOW_PRIORITY = ofproto_v1_3_parser.UINT16_MAX


class CustomSwitchAPI(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {
        'dpset': dpset.DPSet
        # 'wsgi': WSGIApplication
    }

    def __init__(self, *args, **kwargs):
        super(CustomSwitchAPI, self).__init__(*args, **kwargs)

        self.dpset = kwargs['dpset']
        # wsgi = kwargs['wsgi']
        self.waiters = {}
        self.data = {}
        self.data['dpset'] = self.dpset
        self.data['waiters'] = self.waiters

    # mapper = wsgi.mapper
    # wsgi.registory['CustomSwitchController'] = self.data
    # path = '/custom_switch'
    #
    # uri = path + '/module/status'
    # mapper.connect('custom_switch', uri,
    #                controller=CustomSwitchController, action='get_status',
    #                conditions=dict(method=['GET']))
    #
    # uri = path + '/vlan/{switchid}'
    # mapper.connect('custom_switch', uri,
    #                controller=CustomSwitchController, action='get_vlan_status',
    #                conditions=dict(method=['GET']))
    #
    # uri = path + '/set_vlan/{switchid}'
    # mapper.connect('custom_switch', uri,
    #                controller=CustomSwitchController, action='set_vlan_rules',
    #                conditions=dict(method=['POST']))


    @set_ev_cls(dpset.EventDP, dpset.DPSET_EV_DISPATCHER)
    def handle_datapath(self, ev):
        if ev.enter:
            CustomSwitchController.regist_ofs(dp=ev.dp, ports=ev.ports)
            self.add_miss_match(ev)
        else:
            CustomSwitchController.unregist_ofs(ev.dp)

            # CustomSwitchController.get_ofs(ev.dp).config_vlan([1],100,'access')
            # CustomSwitchController.get_ofs(ev.dp).config_vlan([2],100,'access')
            # CustomSwitchController.get_ofs(ev.dp).config_vlan([3],100,'trunk')

    def add_miss_match(self, ev):
        datapath = ev.dp
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    def stats_reply_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath

        if dp.id not in self.waiters:
            return
        if msg.xid not in self.waiters[dp.id]:
            return
        lock, msgs = self.waiters[dp.id][msg.xid]
        msgs.append(msg)

        flags = 0
        # if dp.ofproto.OFP_VERSION == ofproto_v1_0.OFP_VERSION or \
        #     dp.ofproto.OFP_VERSION == ofproto_v1_2.OFP_VERSION:
        # flags = dp.ofproto.OFPSF_REPLY_MORE
        # elif dp.ofproto.OFP_VERSION == ofproto_v1_3.OFP_VERSION:
        flags = dp.ofproto.OFPMPF_REPLY_MORE

        if msg.flags & flags:
            return
        del self.waiters[dp.id][msg.xid]
        lock.set()

    @set_ev_cls(ofp_event.EventOFPErrorMsg, [HANDSHAKE_DISPATCHER, CONFIG_DISPATCHER, MAIN_DISPATCHER])
    def handle_errormsg(self, ev):
        msg = ev.msg
        print ('OFPErrorMsg received')

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _handle_patcketin(self, ev):
        print "msg in"

    # CustomSwitchController.get_ofs(ev.msg.datapath).handle_input_msg(ev)


    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _stats_reply_handler(self, ev):
        self.stats_reply_handler(ev)


class CustomSwitchController(ControllerBase):
    _OFS_LIST = CustomSwitchDict()
    _LOGGER = None

    def __index__(self):
        pass

    def __init__(self, req, link, data, **config):
        super(CustomSwitchController, self).__init__(req, link, data, **config)
        self.dpset = data['dpset']
        self.waiters = data['waiters']

    @classmethod
    def set_logger(cls, logger):
        cls._LOGGER = logger
        cls._LOGGER.propagate = False
        hdlr = logging.StreamHandler()
        fmt_str = '[CC][%(levelname)s] %(message)s'
        hdlr.setFormatter(logging.Formatter(fmt_str))
        cls._LOGGER.addHandler(hdlr)

    @staticmethod
    def regist_ofs(**kwargs):
        dp = kwargs['dp']
        ports = kwargs['ports']
        dpid = dpid_lib.dpid_to_str(dp.id)
        sw = CustomSwitch(dp)
        for p in ports:
            sw.add_custom_port(p)

        CustomSwitchController._OFS_LIST.setdefault(dpid, sw)

    @staticmethod
    def unregist_ofs(dp):
        dpid = dpid_lib.dpid_to_str(dp.id)
        if CustomSwitchController._OFS_LIST.has_key(dpid):
            del CustomSwitchController._OFS_LIST[dpid]
            print "ovs leave controller dpid:%s" % (dpid)

    @staticmethod
    def get_ofs(dp):
        return CustomSwitchController._OFS_LIST.get_ofs(dp.id)

    def get_status(self, req, **_kwargs):
        return self._access_module(REST_ALL, 'get_status',
                                   waiters=self.waiters)

    def get_vlan_status(self, req, **kwargs):
        return self._get_vlan_status(int(kwargs['switchid']))

    def set_vlan_rules(self, req, switchid, **kwargs):
        return self._set_vlan_rules(switchid, req.body)

    def _set_vlan_rules(self, switchid, body):
        try:
            sw = self._OFS_LIST.get_ofs(int(switchid))
        except ValueError as message:
            return Response(status=400, body=str(message))

        try:
            body = json.loads(body)
        except Exception:
            return Response(status=400, body=str("error params format"))

        sw.config_vlan(body['port_no'], body['vlan_id'], body['port_type'])

        return Response(status=200, body=str('ok'))

    def _get_vlan_status(self, switchid):
        try:
            sw = self._OFS_LIST.get_ofs(switchid)
        except ValueError as message:
            return Response(status=400, body=str(message))

        res = {'port_to_vlan': sw.port_to_vlan, 'vlan_mac_table': sw.vlan_mac_table, 'vlan_to_port': sw.vlan_to_port}
        body = json.dumps(res)

        return Response(content_type='application/json', body=body)

    def _access_module(self, switchid, func, waiters=None):
        try:
            dps = self._OFS_LIST.get_ofs(switchid)
        except ValueError as message:
            return Response(status=400, body=str(message))

        msgs = []
        for f_ofs in dps.values():
            function = getattr(f_ofs, func)
            msg = function() if waiters is None else function(waiters)
            msgs.append(msg)

        body = json.dumps(msgs)
        return Response(content_type='application/json', body=body)
