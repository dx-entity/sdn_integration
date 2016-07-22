
import sys
import eventlet

from mq_adapter.TaskReceiver import TaskReceiver

from config_init import GetSingletonConf

from LogFormater import get_logger

from entity_access.EntityAccess import EntityAccess
from global_view.global_statics import GlobalCaseInfo


def global_init():
    # TODO: check b_access_switch, get access port number; refresh b_access_switch; put this info in GlobalCaseInfo
    pass


def main():
    con_file = './apps/parabola/config.conf'
    # print con_file
    CONF = GetSingletonConf.get_conf()

    log_main = get_logger(__name__)

    CONF(default_config_files=[con_file])

    gci = GlobalCaseInfo.get_instance()
    gci.add_entity_entry(CONF.ENTITY_ENTRY.ip, EntityAccess(CONF.ENTITY_ENTRY.ip))

    global_init()

    ##start basic config##
    # log_main.info('start openflow controller')
    # controller = multiprocessing.Process(target=start_of_controller, args=(CONF.of_controller,))
    # controller.start()
    # print controller.pid
    # useful
    # ovs_manager = OvsManager.get_instance()
        # ovs_manager.add_container(CONF.ENTITY_ENTRY.ip, CONF.ENTITY_ENTRY.port)
    #
    # ovs_manager.add_container('127.0.0.1', '6640')
    log_main.info(msg='start receive task from MCU')

    taskrecv = TaskReceiver.get_instance(CONF.MQ_SERVER)

    pool = eventlet.GreenPool()
    while True:
        pool.spawn(taskrecv.receive_forever)

    # get_global()


    # LOG.info('rest start')
    # run_rest_api()


if __name__ == '__main__':
    main(sys.argv)