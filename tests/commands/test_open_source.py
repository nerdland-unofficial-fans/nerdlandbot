import pytest

from tests.conftest import testbot

@pytest.mark.asyncio
async def test_open_source_default(testbot):
    ctx, message_mock = await testbot.command(message="!open_source")

    message_mock.send_message.assert_called_once()

    assert ctx.command.name == "open_source"


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["!os", "!opensource"])
async def test_open_source_aliasses(testbot, message):
    ctx, message_mock = await testbot.command(message=message)

    message_mock.send_message.assert_called_once()

    assert ctx.command.name == "open_source"
