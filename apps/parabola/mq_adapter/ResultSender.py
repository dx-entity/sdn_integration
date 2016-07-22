import stomp
from apps.parabola.config_init import GetSingletonConf

CONF = GetSingletonConf.get_conf()


class ResultSender(object):

    _res_sender = None

    def __init__(self):
        self.MQCONF = None
        self.get_conn()

    @staticmethod
    def get_instance():
        if not ResultSender._res_sender:
            ResultSender._res_sender = ResultSender()
        return ResultSender._res_sender

    def get_conn(self):
        self.MQCONF = CONF.MQ_SERVER
        server_ip = self.MQCONF.ip
        server_port = self.MQCONF.port
        self.conn = stomp.Connection([(server_ip, server_port)])
        self.conn.start()
        self.conn.connect('admin', 'password', wait=True)

    def send_msg(self, msg, task=True):
        if not self.conn.is_connected():
            self.get_conn()
        if task:
            self.conn.send(body=str(msg), destination='/topic/'+self.MQCONF.E2MTopic)
        else:
            self.conn.send(body=str(msg), destination='/topic/'+self.MQCONF.M2EHeartTopic)