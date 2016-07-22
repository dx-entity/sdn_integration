##ovs port type

#ovs static string
INTERNAL = 'internal'
PATCH = 'patch'
VXLAN = 'vxlan'
TRUNK = 'trunk'

class OVS():
    MANAGERPORT = "6640"
    class EntityAccess():
        INTERFACE = 'eth1'
        TRUNK = str([i for i in range(0, 1000, 100)][1:])
    class PortType():
        INTERNAL = 'internal'
        PATCH = 'patch'
        VXLAN = 'vxlan'
        TRUNK = 'trunk'
    class OVSType():
        ACCESS = "access"
        AGENT = "agent"

#xml static string
REALHOST = 'real_host'
REALSERVER = 'real_server'
REALSWITCH = 'real_switch'
NODEID = 'id'
NODEINTERFACE = 'interface'
NODELINK = 'link'
LINKNODETYPE = 'type'

class CASESTATE():
    CASEDEFINED = '200501'
    CASECLOSED = '200506'

class XML():
    REALHOST = 'real_host'
    REALSERVER = 'real_server'
    REALSWITCH = 'real_switch'
    NODEID = 'id'
    NODEINTERFACE = 'interface'
    NODELINK = 'link'
    LINKNODETYPE = 'type'


#nfs static string
class NFS():
    NFSBASE='/mnt/FileServer/'


#msg static string
class MSG():
    CASEID = "caseid"
    TASKNAME = "name"
    TASKID = "taskid"
    TASKTYPE = "type"
    SERVERIP = "server_ip"
    DEFINE = "define"
    TFILE = "tfile"
    TASKTODO = "M"
    TASKBACK = "F"
    IPADDR = "ipaddr"
    ID = "id"
    MODULENAME = "ec"
    RESULT = "result"
    class RES():
        CONCLUSION = "conclusion"
        DONE = "done"
        NEED = "need"
        DESCRIPTION = "description"
#vxlan info
class VXLANINFO():
    MAXVXLANID=16777216
    MINVXLANID=100
