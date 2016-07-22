from ryu.ofproto import ofproto_v1_3
from ryu.ofproto import ofproto_v1_3_parser
from ryu.ofproto import ofproto_v1_2
from ryu.ofproto import ofproto_v1_2_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto import ofproto_v1_0_parser

class Vlan(object):

	VLANID_MIN = 2
	VLANID_MAX = 4094

	VLAN_ACCESS='access'
	VLAN_TRUNK='trunk'
	VLAN_DEFAULT = '0'

	def __init__(self):
		super(Vlan, self).__init__()

	def _push_vlan_action(self,vlan_vid=0x0000, parser=ofproto_v1_3_parser):
		return [parser.OFPActionPushVlan(),
				parser.OFPActionSetField(vlan_vid=(ofproto_v1_3.OFPVID_PRESENT | vlan_vid))]

	def _pop_vlan_action(self,parser=ofproto_v1_3_parser):
		return [parser.OFPActionPopVlan()]

	def _vlan_msg_flood(self, port=[], parser=ofproto_v1_3_parser):
		if not port:
			actions = []
			for pn in port:
				actions.append(parser.OFPActionOutput(pn.port_no))
		return actions

	def get_access_port_rule(self,port_no=0, vlan_vid=0, vlan_port=[], trunk_port=[], parser=ofproto_v1_3_parser):
		res={'un-access':[],'un-trunk':[],'tag-access':[],'tag-trunk':[]}

		match_untagged = [parser.OFPMatch(in_port=port_no)]

		if vlan_port:
			res['un-access'].append(match_untagged)
			actions_untagged_to_access = []
			for port in vlan_port:
				if port_no == port:
					continue
				actions_untagged_to_access.append(parser.OFPActionOutput(port))
			res['un-access'].append(actions_untagged_to_access)

		if trunk_port:
			res['un-trunk'].append(match_untagged)
			actions_untagged_to_trunk = []
			actions_untagged_to_trunk += self._push_vlan_action(vlan_vid)
			for port in trunk_port:
				if port_no == port:
					continue
				actions_untagged_to_trunk.append(parser.OFPActionOutput(port))
			res['un-trunk'].append(actions_untagged_to_trunk)


		match_tagged = [parser.OFPMatch(in_port=port_no, vlan_vid=ofproto_v1_3.OFPVID_PRESENT|vlan_vid)]
		if vlan_port:
			res['tag-access'].append(match_tagged)
			actions_tagged_to_access = []
			actions_tagged_to_access += self._pop_vlan_action()
			for port in vlan_port:
				if port_no == port:
					continue
				actions_tagged_to_access.append(parser.OFPActionOutput(port))
			res['tag-access'].append(actions_tagged_to_access)

		if trunk_port:
			res['tag-trunk'].append(match_tagged)
			actions_tagged_to_trunk = []
			for port in trunk_port:
				if port_no == port:
					continue
				actions_tagged_to_trunk.append(parser.OFPActionOutput(port))
			res['tag-trunk'].append(actions_tagged_to_trunk)

		return res

