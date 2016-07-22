

from ryu.ofproto import ofproto_v1_3

from ryu.topology import switches
from BasicElement import BasicElement

class CustomPort(switches.Port, BasicElement):


    def __init__(self,dpid, ofproto, ofpport):
        super(CustomPort, self).__init__(dpid, ofproto, ofpport)
        self.vlan_port_type=None
        self.vlan_port_vid=ofproto_v1_3.OFPVID_NONE


    def get_vlan_details(self):
        return {'vlan_port_type':self.vlan_port_type,'vlan_port_vid':self.vlan_port_vid,'port_no':self.port_no}