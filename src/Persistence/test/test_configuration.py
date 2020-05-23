import os

import pytest

from Persistence.configuration import Configuration
from Persistence.json.jsonconfigstore import JsonConfigStore

JSON = 'test_config.json'
DATA = {'key': 'value'}


@pytest.fixture(autouse=True)
def wrap():
    clean()
    yield
    clean()


def clean():
    if os.path.exists(JSON):
        os.remove(JSON)


def test_get_keys():
    dumper = JsonConfigStore(JSON)
    configuration = Configuration(dumper)
    dumper.write(DATA)
    assert configuration.get_keys() == DATA.keys()


def test_put():
    dumper = JsonConfigStore(JSON)
    configuration = Configuration(dumper)
    configuration.put('key', 'value')
    assert dumper.read() == {'key': 'value'}


def test_get():
    dumper = JsonConfigStore(JSON)
    configuration = Configuration(dumper)
    configuration.put('key', 'value')
    assert configuration.get('key') == 'value'
