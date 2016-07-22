from abc import ABCMeta, abstractmethod
import apps.parabola.static as data
import json


class BaseMsgGenerator(object):

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def get_msg(self):
        pass


class TaskMsgGenerator(BaseMsgGenerator):

    def __init__(self, case_id, task_id, msg_type, server_ip, name, res=None):
        #TODO add res dict
        self.msg = dict()
        self.msg[data.MSG.CASEID] = case_id
        self.msg[data.MSG.TASKID] = task_id
        self.msg[data.MSG.SERVERIP] = server_ip
        self.msg[data.MSG.TASKTYPE] = msg_type
        self.msg[data.MSG.TASKNAME] = name
        self.res = dict()
        if not res:
            res[data.MSG.RES.CONCLUSION] = 1
            res[data.MSG.RES.DESCRIPTION] = ""
            res[data.MSG.RES.DONE] = 0
            res[data.MSG.RES.NEED] = 0
            self.msg[data.MSG.RESULT] = res

    def get_msg(self):
        return json.dumps(self.msg)


class HeartBeatMsgGenerator(BaseMsgGenerator):

    def __init__(self, id, ipaddr, name, type):
        pass

    def get_msg(self):
        pass
