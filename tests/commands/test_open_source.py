import pytest

@pytest.mark.asyncio
async def test_open_source_default(nerdlandbot):
    ctx, message_mock = await nerdlandbot.command(message="!open_source")

    message_mock.send_message.assert_called_once()

    assert ctx.command.name == "open_source"


@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["!os", "!opensource"])
async def test_open_source_aliasses(nerdlandbot, message):
    ctx, message_mock = await nerdlandbot.command(message=message)

    message_mock.send_message.assert_called_once()

    assert ctx.command.name == "open_source"
