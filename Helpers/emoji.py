from discord.ext import commands

thumbs_up = "👍"
thumbs_down = "👎"
white_check_mark = "✅"
scales = "⚖️"
trophy = "🏆"

flags = {
    "nl": "🇳🇱",
    "en": "🇬🇧"
}


def get_custom_emoji(ctx: commands.Context, emoji_id: int) -> str:
    """
    Returns a custom emoji by id as <:name:id>
    :param ctx: The current context. (discord.ext.commands.Context)
    :param emoji_id: The id of the custom emoji: (str)
    :return: The emoji, formatted for a discord message. (str)
    """
    custom_emoji = ctx.bot.get_emoji(emoji_id).name
    return f'<:{custom_emoji}:{emoji_id}>'
