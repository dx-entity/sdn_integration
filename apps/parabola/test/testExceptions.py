import traceback
import logging
import os
import sys

# logging.basicConfig(format="[%(asctime)s] %(name)s {%(filename)s:line %(lineno)d} %(levelname)s: %(message)s", steam=sys.stdout, level=logging.DEBUG)
# log = logging.getLogger(__name__)
#
# try:
#     raise NameError
# except Exception, e:
#     log.exception('exception')


class CaseException(KeyError):

    def __init__(self, *args, **kwargs):
        super(CaseException, self).__init__(args, kwargs)
        if args:
            self.message = args[0]

# print help(traceback)

a = {'a': 'c'}

# try:
#     raise NameError("name not found")
# except Exception, e:
#     print e.__class__.__name__
#     print e.message
    # print str(Exception.message)


def exception_handler(func):
    def _handler(*args, **kwargs):
        try:
            func(*args, **kwargs)
        # except EOFError, e:
        #     print e.__class__.__name__
        #     print e.message
        #     print traceback.print_exc()
        except Exception, e:
            # print e.__class__.__name__
            # print e.message
            # print traceback.format_stack()
            # log.info(e.message)
            pass
    return _handler


@exception_handler
def kk(a):
    raise CaseException("has no such case registered")

kk(a)

