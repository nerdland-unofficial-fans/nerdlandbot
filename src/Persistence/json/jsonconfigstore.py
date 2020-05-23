import json
from abc import ABC

from Persistence.abstractconfigstore import ConfigStore


class JsonConfigStore(ConfigStore, ABC):

    __filename = ""

    def __init__(self, filename='config.json'):
        self.__filename = filename
        self.validate()

    def validate(self):
        with open(self.__filename, 'w+') as file:
            file.write('{}')

    def read(self):
        with open(self.__filename, 'r') as file:
            return json.loads(file.read())

    def write(self, data):
        with open(self.__filename, 'r+') as file:
            json.dump(data, file)
