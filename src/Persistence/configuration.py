class Configuration:

    config_store = None

    def __init__(self, config_store):
        self.config_store = config_store

    def __get_data(self):
        return self.config_store.data

    def __set_data(self, data):
        self.config_store.data = data

    def refresh(self):
        self.__set_data(self.config_store.read())

    def get(self, key):
        self.refresh()
        return self.__get_data()[key]

    def put(self, key, value):
        self.refresh()
        self.__get_data()[key] = value
        self.config_store.write(self.__get_data())

    def get_keys(self):
        self.refresh()
        return self.__get_data().keys()
