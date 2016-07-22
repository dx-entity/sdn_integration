from xml.etree import ElementTree as ET

import apps.parabola.static as data


class XMLAnalyser(object):
    """
    1. analyse xml
    2. find the node connect to real node (currently support real host, switch, server)
    3. generate a json data and send to ovs_adapter

    the res is formatted in follow:
    [{'node_id':'123', 'node_type':'real_host',
      'node_link':[{'node_id':'234', 'node_type':'emu_switch'},.....]
    },.....]
    """

    def __init__(self, xmlfilepath):
        self.xmlfilepath = xmlfilepath

    def xml_analyser(self):
        tree = ET.ElementTree(file=self.xmlfilepath)

        real_host = tree.iter(tag=data.REALHOST)
        real_server = tree.iter(tag=data.REALSERVER)
        real_switch = tree.iter(tag=data.REALSWITCH)

        res = map(self.collector_analyse, [real_host, real_server, real_switch])

        final = []
        for r in res:
            final += r
        return final

    def collector_analyse(self, collector):
        res = []
        for node in collector:
            info_temp = {'node_id': None, 'node_type': None, 'node_link': []}
            info_temp['node_id'] = node.attrib.get(data.NODEID, None)
            info_temp['node_type'] = node.tag

            for interface in node.iter(tag=data.NODEINTERFACE):
                link_temp = {'node_id': None, 'node_type': None}
                link = interface.find(data.NODELINK)
                link_temp['node_type'] = link.get(data.LINKNODETYPE)
                link_temp['node_id'] = link.text
                info_temp['node_link'].append(link_temp)
            res.append(info_temp)
        return res






