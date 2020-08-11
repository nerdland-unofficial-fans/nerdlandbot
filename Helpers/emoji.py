from discord.ext import commands


def get_custom_emoji(ctx: commands.Context, emoji_id: str) -> str:
    custom_emoji = ctx.bot.get_emoji(int(emoji_id)).name
    return f'<:{custom_emoji}:{emoji_id}>'
