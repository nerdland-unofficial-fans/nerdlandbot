from abc import ABC, abstractmethod


class ConfigStore(ABC):

    data = {}

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, data: dict):
        pass
