import sys
sys.path.append('/root/parabola')

from ovs_manager.OvsManager import OvsManager

import tornado.ioloop
import tornado.web
import json

REST_ALL='all'

_ovs_manager = OvsManager.get_instance()

class OvsManagerAccess(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        if len(args) == 1:
            con_ip = args[0]
            if con_ip:
                container = _ovs_manager.get_container(con_ip)
                self.write(str(container))
            else:
                container = _ovs_manager.get_all()
                ret = ''
                for k, v in container.iteritems():
                    ret += (k+'\n')
                self.write(ret)
        else:
            pass
        # self.write("args:"+str(args))

    def post(self, *args, **kwargs):
        if len(args) != 2:
            self.write_error(404)

        con_ip = args[0]
        con_port = args[1]
        container = _ovs_manager.add_container(con_ip=con_ip, con_port=con_port)
        detail = str(container)
        self.write(detail)


class OvsContainerAccess(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        if len(args) != 2:
            self.write_error(404)

        container = _ovs_manager.get_container(args[0])
        if not container:
            self.write_error(404)

        if args[1]==REST_ALL:
            res = container.br_list
        else:
            res = container.get_br(args[1])

        beauty_output = json.dumps(str(res), indent=2)
        self.write(beauty_output)

    def post(self, *args, **kwargs):
        pass


class OvsBrAccess(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        if len(args) != 2:
            self.write_error(404)

        container = _ovs_manager.get_container(args[0])
        if not container:
            self.write_error(404)

        if args[1] == REST_ALL:
            res = container.br_list
        else:
            res = container.get_br(args[1])

        beauty_output = json.dumps(str(res), indent=2)
        self.write(beauty_output)

        pass

    def post(self, *args, **kwargs):
        pass

application = tornado.web.Application([
    (r"/manager/register/(.*)/(.*)", OvsManagerAccess),
    (r"/manager/getter/(.*)", OvsManagerAccess),
    (r"/container/add_br/(.*)/(.*)", OvsContainerAccess),
    (r"/container/get_br/(.*)/(.*)", OvsContainerAccess),
    (r"/br/get_port/(.*)", OvsBrAccess),
    (r"/br/add_port/(.*)", OvsBrAccess),
])

def run_rest_api():
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()