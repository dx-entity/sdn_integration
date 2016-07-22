

class BasicElement(object):
    def __init__(self):
        self.id = None

    def getNodeType(self):
        return self.__class__.__name__.lstrip('Custom').lower()