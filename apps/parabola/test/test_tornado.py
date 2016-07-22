import tornado.ioloop
import tornado.web
import json
class hello(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello'+self.get_argument('a'))
        self.write('Hello'+self.get_argument('b'))
class add(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello'+str(args)+str(kwargs))

    def post(self):
        res = Add(json.loads(self.request.body))
        self.write(json.dumps(res))

class a(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write('Hello'+str(args)+str(kwargs))
def Add(input):
    sum = input['num1'] + input['num2']
    result = {}
    result['sum'] = sum
    return result
application = tornado.web.Application([
    (r"/", hello),
    (r"/add/(.*)", add),
    (r"/a/(.*)/(.*)", add),
])
if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()