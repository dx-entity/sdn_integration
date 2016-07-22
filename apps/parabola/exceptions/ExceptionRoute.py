

def exception_handler(func):
    def _handler(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except EOFError, e:
            print e.__class__.__name__
            print e.message
        except Exception, e:
            print e.__class__.__name__
            print e.message
    return _handler