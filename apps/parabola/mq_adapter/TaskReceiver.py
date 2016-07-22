import stomp

from apps.parabola.LogFormater import get_logger
from apps.parabola.mq_adapter.TaskRouter import TaskRouter


class TaskReceiver(object):

    _instance = None

    def __init__(self, MQCON):
        self.MQCON = MQCON
        self.connect()

    def connect(self):
        server_ip = self.MQCON.ip
        server_port = self.MQCON.port
        self.conn = stomp.Connection([(server_ip, server_port)])
        taskhandler = TaskHandler()
        self.conn.set_listener('', taskhandler)
        self.conn.start()
        self.conn.connect('admin', 'password', wait=True)

        self.conn.subscribe(destination='/topic/' + self.MQCON.M2ETopic, id=1, ack='auto')


    @staticmethod
    def get_instance(con):
        if not TaskReceiver._instance:
            TaskReceiver._instance = TaskReceiver(con)

        return TaskReceiver._instance

    def receive_forever(self):
        if not self.conn.is_connected():
            self.connect()


class TaskHandler(stomp.ConnectionListener):

    def __init__(self):
        self.LOG_TASK_HANDLER = get_logger(self.__class__.__name__)

    def on_error(self, headers, message):
        print 'receive an error %s' % (message)

    def on_message(self, headers, message):
        if message:
            self.LOG_TASK_HANDLER.info(message)

        # try:
        TaskRouter.deliver_task(message)
        # except Exception, e:
            # print e
            # self.LOG_TASK_HANDLER.exception(e)
            # return
        # print 'receive a message %s' % (message)


class HeartbeatReceiver(object):

    _instance = None

    def __init__(self, MQCON):
        self.MQCON = MQCON
        self.connect()

    def connect(self):
        server_ip = self.MQCON.ip
        server_port = self.MQCON.port
        self.conn = stomp.Connection([(server_ip, server_port)])
        heartbeathandler = HeartbeatHandler()
        self.conn.set_listener('', heartbeathandler)
        self.conn.start()
        self.conn.connect('admin', 'password', wait=True)

        self.conn.subscribe(destination='/topic/' + self.MQCON.M2EHeartTopic, id=1, ack='auto')

    @staticmethod
    def get_instance(con):
        if not HeartbeatReceiver._instance:
            HeartbeatReceiver._instance = HeartbeatReceiver(con)

        return HeartbeatReceiver._instance

    def receive_forever(self):
        if not self.conn.is_connected():
            self.connect()


class HeartbeatHandler(stomp.ConnectionListener):
    def __init__(self):
        self.LOG_TASK_HANDLER = get_logger(self.__class__.__name__)

    def on_error(self, headers, message):
        print 'receive an error %s' % (message)

    def on_message(self, headers, message):
        if message:
            self.LOG_TASK_HANDLER.info(message)

        TaskRouter.deliver_task(message)