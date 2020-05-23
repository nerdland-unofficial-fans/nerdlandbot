import os

import pytest

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


def test_init():
    JsonConfigStore(JSON)


def test_write():
    dumper = JsonConfigStore(JSON)
    dumper.write(DATA)
    with open(JSON, 'r') as file:
        assert file.read() == '{"key": "value"}'


def test_read():
    dumper = JsonConfigStore(JSON)
    dumper.write(DATA)
    assert dumper.read() == DATA
