import MySQLdb
from apps.parabola.config_init import GetSingletonConf

CONF = GetSingletonConf.get_conf()

class DBConnector(object):
    _instance = None

    def __init__(self):
        self.DBCONF = CONF.MYSQL_DB

    def get_conn(self):
        conn = MySQLdb.connect(self.DBCONF.ip, self.DBCONF.username, self.DBCONF.password, self.DBCONF.db, charset='utf8')
        return conn.cursor()

    def do_query(self, sql):
        mydb = self.get_conn()
        mydb.execute(sql)
        return mydb.fetchall()

    def insert_one(self, sql):
        conn = self.get_conn()
        conn.execute('begin')
        num = conn.execute(sql)
        conn.execute('commit')
        conn.close()

    def update_all(self, sql):
        conn = self.get_conn()
        conn.execute('begin')
        num = conn.execute(sql)
        conn.execute('commit')
        conn.close()