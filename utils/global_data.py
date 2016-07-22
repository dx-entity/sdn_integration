class GlobalData(object):

    _instance = None

    def __init__(self):
        self.data = {}
        self.app_info = {}
        self.app_status = {}

    @staticmethod
    def get_instance():
        if not GlobalData._instance:
            GlobalData._instance = GlobalData()
        return GlobalData._instance
