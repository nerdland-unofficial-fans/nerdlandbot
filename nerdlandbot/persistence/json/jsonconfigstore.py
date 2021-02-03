import json
import os
from abc import ABC

from nerdlandbot.persistence.abstractconfigstore import ConfigStore


class JsonConfigStore(ConfigStore, ABC):

    _filename = ""

    def __init__(self, filename='config.json'):
        self._filename = filename
        self.validate()

    def validate(self):
        if not os.path.exists(self._filename):
            with open(self._filename, 'w') as file:
                file.write('{}')

    def read(self):
        with open(self._filename, 'r') as file:
            return json.loads(file.read())

    def write(self, data: dict):
        with open(self._filename, 'w') as file:
            json.dump(data, file)
