from oslo_config import cfg

opts = [
    cfg.StrOpt('of_controller', default='openflow_controller/CustomController.py')
]

ovs_entity_group = cfg.OptGroup(name='ENTITY_ENTRY', title='ovs-container list')

ovs_container_Opts = [
    cfg.StrOpt('ip',
               default='172.16.21.144',
               help='ovs container ip'
               ),
    cfg.StrOpt('port',
               default='6640',
               help='Port number to listen on.')
]

mq_server_group = cfg.OptGroup(name='MQ_SERVER', title='mq_server configurations')

mq_server_Opts = [
    cfg.StrOpt('ip',
               default='172.16.21.94',
               help='activemq server ip'
               ),
    cfg.StrOpt('port',
               default='61613',
               help='Port number to connect to mq server.'),
    cfg.StrOpt('M2ETopic',
               default='MCU2ECUMessageTopic',
               help='MCU2ECU msg topic.'),
    cfg.StrOpt('E2MTopic',
               default='ECU2MCUMessageTopic',
               help='ECU2MCU msg topic.'),
    cfg.StrOpt('M2EHeartTopic',
               default='MCU2ECUHeartBeatTopic',
               help='MCU2ECU HeartBeat Topic.'),
    cfg.StrOpt('E2MHeartTopic',
               default='ECU2MCUHeartBeatTopic',
               help='ECU2MCU HeartBeat Topic.')
]

mysql_server_group = cfg.OptGroup(name='MYSQL_DB', title='mysql configurations')

mysql_server_Opts = [
    cfg.StrOpt('ip',
               default='172.16.21.252',
               help='mysql server ip'
               ),
    cfg.StrOpt('username',
               default='root',
               help='Port number to connect to mysql server.'),
    cfg.StrOpt('password',
               default='iiecas',
               help='Port number to connect to mysql server.'),
    cfg.StrOpt('db',
               default='bc',
               help='mysql database name.')
]

log_conf_group = cfg.OptGroup(name='LOG_CONFIG', title='log configuration')

log_conf_Opts = [
    cfg.BoolOpt('debug',
                default=True,
                help='debug info level'
                ),
    cfg.StrOpt('log_date_format',
               default='[%(asctime)s] %(name)s <%(filename)s:line %(lineno)d> %(levelname)s: %(message)s',
               help='log format')
]

CONF = cfg.CONF
CONF.register_opts(opts)
CONF.register_group(ovs_entity_group)
CONF.register_opts(ovs_container_Opts, ovs_entity_group)
CONF.register_group(mq_server_group)
CONF.register_opts(mq_server_Opts, mq_server_group)
CONF.register_group(mysql_server_group)
CONF.register_opts(mysql_server_Opts, mysql_server_group)
CONF.register_group(log_conf_group)
CONF.register_opts(log_conf_Opts, log_conf_group)


class GetSingletonConf(object):
    _instance = None

    @staticmethod
    def get_conf():
        if not GetSingletonConf._instance:
            GetSingletonConf._instance = CONF
        return GetSingletonConf._instance
