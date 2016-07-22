
from ryu.exception import OFPUnknownVersion

from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
from ryu.lib import dpid as dpid_lib
from ryu.topology import switches
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

from openflow_controller.Vlan import Vlan
from openflow_controller.StaticData import *
from openflow_controller.TableManager import table

from BasicElement import BasicElement

class CustomSwitchDict(dict):
	def __init__(self):
		super(CustomSwitchDict, self).__init__()

	def get_ofs(self, dpid):
		if len(self) == 0:
			raise ValueError('no ovs is connected')
		if dpid == REST_ALL:
			dps = self
			return dps
		else:
			try:
				dp_id = dpid_lib.dpid_to_str(dpid)
			except:
				raise ValueError('Invalid switchID.')
			if self.has_key(dp_id):
				return self[dp_id]


class CustomSwitch(switches.Switch, BasicElement):

	_SUP_VLAN_PORT_TYPE=[Vlan.VLAN_ACCESS, Vlan.VLAN_TRUNK]

	_OFCTL = {ofproto_v1_3.OFP_VERSION: ofctl_v1_3}

	_VLAN_DEFAULT = Vlan.VLAN_DEFAULT

	def __init__(self, dp):
		super(CustomSwitch, self).__init__(dp)
		self.dpid_str = dpid_lib.dpid_to_str(self.dp.id)
		self.vlan_to_port = {}
		self.port_to_vlan = {}
		self.vlan_mac_table = {Vlan.VLAN_DEFAULT:{}}

		self.dp = dp
		version = dp.ofproto.OFP_VERSION
		if version not in self._OFCTL:
			raise OFPUnknownVersion(version=version)
		self.ofctl = ofctl_v1_3


	def add_custom_port(self, ofpport):
		port = CustomPort(self.dp.id, self.dp.ofproto, ofpport)
		if not self.vlan_to_port.has_key(self._VLAN_DEFAULT):
			self.vlan_to_port[self._VLAN_DEFAULT] = []
		self.vlan_to_port[self._VLAN_DEFAULT].append([port.port_no])
		if not port.is_reserved():
			self.ports.append(port)


	def _get_port(self,port_no):
		ports=[]
		for port in self.ports:
			if port_no==port.port_no:
				ports.append(port)
		if not len(ports):
			raise ValueError("switch %s has no port %s"%(self.dpid_str, port_no))
		return ports

	def config_vlan(self, ports, vlan_id, port_type):

		if len(ports) > 1:
			'''
			TODO:
				tmp not support,batch add vlan
				yeild to do this later
			'''
			return

		elif len(ports) == 0:
			raise ValueError("invalidate port num")

		for port in ports:
			p = self._get_port(port)

		if not(type(vlan_id) == type(1) and vlan_id < Vlan.VLANID_MAX and vlan_id > Vlan.VLANID_MIN):
			raise ValueError("vlan_id not suitable")

		if not port_type in self._SUP_VLAN_PORT_TYPE:
			raise ValueError("vlan_type:%s is not supported"%(port_type))

		def update_data(self):
			pass

		if not self.vlan_to_port.has_key(str(vlan_id)):
			self.vlan_to_port[str(vlan_id)] = []
		if not self.vlan_mac_table.has_key(str(vlan_id)):
			self.vlan_mac_table[str(vlan_id)] = {}

		for port in p:
			port.vlan_port_type=port_type
			port.vlan_port_vid=vlan_id
			item=[port.port_no,port_type]
			if item not in self.vlan_to_port[str(vlan_id)]:
				self.vlan_to_port[str(vlan_id)].append(item)
			if port_type==Vlan.VLAN_ACCESS:
				ori_vlan = self.port_to_vlan.get(str(port.port_no),self._VLAN_DEFAULT)
				self.vlan_to_port[ori_vlan].remove([int(port.port_no)])
				self.port_to_vlan[str(port.port_no)] = vlan_id
			elif port_type==Vlan.VLAN_TRUNK:
				if not self.port_to_vlan.has_key(port.port_no):
					self.port_to_vlan[port.port_no] = []
				if not isinstance(self.port_to_vlan[port.port_no], list):
					self.port_to_vlan[port.port_no] = [self.port_to_vlan[port.port_no]]
				self.port_to_vlan[port.port_no].append(port.port_no)

		# self._config_vlan(vlan_id, port.port_no)


	def get_vlan_info(self):
		res = {"switch_id":self.dpid_str, "port":[]}
		for port in self.ports:
			res["port"].append(port.get_vlan_details())
		return res

	def handle_input_msg(self,ev):
		msg = ev.msg
		datapath = msg.datapath
		parser = datapath.ofproto_parser
		ofproto = datapath.ofproto
		pkt = packet.Packet(msg.data)
		eth_pkt = pkt.get_protocol(ethernet.ethernet)

		dst = eth_pkt.dst
		src = eth_pkt.src
		in_port = str(msg.match['in_port'])
		vlan_id = str(self.port_to_vlan[in_port] if self.port_to_vlan.has_key(in_port) else 0)
		# if dst == 'ff:ff:ff:ff:ff:ff':
		out_port = [p[0] for p in self.vlan_to_port[vlan_id]]
		out_port.remove(int(in_port))

		self.vlan_mac_table[vlan_id][src]=int(in_port)

		vlan_action = Vlan().get_access_port_rule(port_no=int(in_port),vlan_vid=int(vlan_id),vlan_port=out_port)

		self.add_flow(datapath, vlan_action)

		data = None
		if msg.buffer_id == ofproto.OFP_NO_BUFFER:
			data = msg.data

		for p in out_port:
			out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
	                              in_port=int(in_port), actions=[parser.OFPActionOutput(int(p))],
	                              data=data)
			datapath.send_msg(out)

	def rest_command(func):
		def _rest_command(*args, **kwargs):
			key, value = func(*args, **kwargs)
			switch_id = dpid_lib.dpid_to_str(args[0].dp.id)
			return {REST_SWITCHID: switch_id,
		            key: value}
		return _rest_command


	@rest_command
	def get_status(self, waiters):
		msgs = self.ofctl.get_flow_stats(self.dp, waiters)

		status = REST_STATUS_ENABLE
		if str(self.dp.id) in msgs:
			flow_stats = msgs[str(self.dp.id)]
			for flow_stat in flow_stats:
				if flow_stat['priority'] == STATUS_FLOW_PRIORITY:
					status = REST_STATUS_DISABLE

		return REST_STATUS, status


	def add_flow(self,datapath, vlan_action):
		for key in vlan_action:
			if vlan_action[key]:
				match = vlan_action[key][0][0]
				actions = vlan_action[key][1]
				inst = [datapath.ofproto_parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS,
		                                             actions)]
				mod = datapath.ofproto_parser.OFPFlowMod(datapath=datapath, priority=1,
		                                match=match, instructions=inst)
				datapath.send_msg(mod)

