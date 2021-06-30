import os
import pytest

from nerdlandbot import __version__
from tests.conftest import testbot, raw_testbot, NerdlandBot


def test_version():
    assert __version__ == '0.1.0'


def test_prefix_default(testbot):
    assert testbot.command_prefix == '!'


def test_prefix_non_default():
    prefix = '$'
    bot = NerdlandBot(prefix, None)

    assert bot.command_prefix == prefix


def test_prefix_fail():
    os.environ['PREFIX'] = ''
    with pytest.raises(SystemExit):
        raw_testbot()
