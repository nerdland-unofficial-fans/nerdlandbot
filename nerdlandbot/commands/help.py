import discord

from discord.ext import commands

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture

empty = '\u200b'


def build_title(title: str, line_width: int = 30) -> str:
    """
    Draws a separator and prints the title
    :param title: The title to print. (str)
    :param line_width: The width of the separator to draw. (optional - int - default = 30)
    :return: A string containing the separator and title. (str)
    """
    return f"~~-{' ' * line_width}-~~" + '\n' + f"**{title}**" + '\n'


async def send_embed(ctx: commands.Context, embed: discord.Embed):
    """
    Send embed to the current context
    :param ctx: The current context. (discord.ext.commands.Context)
    :param embed: the embed to send back to the current context. (discord.Embed)
    """
    if len(embed) > 0:
        return await ctx.channel.send(embed=embed)

    # if we reach here, the embed is empty and we show an error
    name = empty
    value = translate("help_err_not_recognized", await culture(ctx)).format(ctx.prefix)
    embed.add_field(name=name, value=value, inline=False)
    await ctx.channel.send(ctx, embed)


async def build_commands_message(cog: commands.Cog, current_culture: str) -> str:
    """
    Builds the help info for a certain cog
    :param cog: The requested cog. (discord.ext.commands.Cog)
    :param current_culture: The culture in which the help should be generated (str)
    :return: The help info for the given cog (str)
    """

    message = {}
    for command in cog.get_commands():
        if command.hidden:
            continue

        if command.brief is None:
            message[command.name] = translate(command.help, current_culture)
        else:
            message[command.name] = translate(command.brief, current_culture)

    strings = []
    for name in sorted(message):
        strings.append("*{0}*\n \u2003 {1}\n".format(name, message[name]))

    return ' '.join(strings)


async def general_help(ctx: commands.Context):
    """
    Builds and sends the general help info to the current context.
    :param ctx: The current context. (discord.ext.commands.Context)
    """
    embed = discord.Embed()

    for cog_name in ctx.bot.cogs:
        content = await build_commands_message(ctx.bot.get_cog(cog_name), await culture(ctx))

        if len(content) == 0:
            continue

        title = build_title(cog_name)
        embed.add_field(name=title, value=content, inline=False)

    extra_info_command = translate("help_info_command", await culture(ctx)).format(ctx.prefix)
    extra_info_category = translate("help_info_category", await culture(ctx)).format(ctx.prefix)
    extra_info = f'{extra_info_command}\n{extra_info_category}'
    embed.add_field(name=empty, value=extra_info, inline=False)
    await send_embed(ctx, embed)


async def subject_help(ctx: commands.Context, cog_name: str):
    """
    Builds and sends the help info for the given cog to the current context.
    :param ctx: The current context. (discord.ext.commands.Context)
    :param cog_name: The subject to request help on. (str)
    """
    embed = discord.Embed()
    cog = ctx.bot.get_cog(cog_name)
    content = await build_commands_message(cog, await culture(ctx))

    # add subject title
    title = f'**{cog_name}**\n'
    embed.add_field(name=title, value=content, inline=False)

    # add extra info
    extra_info = translate("help_info_command", await culture(ctx)).format(ctx.prefix)
    embed.add_field(name=empty, value=extra_info, inline=False)

    await send_embed(ctx, embed)


async def command_help(ctx: commands.Context, command_name: str):
    """
    Builds and sends the help info on the given command to the current context.
    :param ctx: The current context. (discord.ext.commands.Context)
    :param command_name: The command to request help on. (str)
    """
    # TODO print aliases
    embed = discord.Embed()

    command = ctx.bot.get_command(str(command_name))

    title = ctx.prefix + command.name
    help_text = translate(command.help, await culture(ctx))

    if command.usage is None:
        title += '\n'
        embed.add_field(name=title, value=help_text, inline=False)
        return await send_embed(ctx, embed)

    title += '\u2000' + translate(command.usage, await culture(ctx)) + '\n'
    embed.add_field(name=title, value=help_text, inline=False)

    extra_info = translate("help_info_arguments", await culture(ctx))
    embed.add_field(name=empty, value=extra_info, inline=False)

    await send_embed(ctx, embed)


class Help(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @commands.command(name='help', hidden=True, usage='help_usage', brief='help_brief', help='help_help')
    async def help(self, ctx: commands.Context, subject: str = None):
        """
        Show the help text for the given subject, or the general help if no subject provided.
        :param ctx: The current context. (discord.ext.commands.Context)
        :param subject: The subject to request help on. (optional - str - default = None)
        """
        if subject is None:
            return await general_help(ctx)

        for cog_name in ctx.bot.cogs:
            if cog_name.lower() == subject.lower():
                return await subject_help(ctx, cog_name)

        for command_name in ctx.bot.commands:
            if str(command_name) == str(subject):
                return await command_help(ctx, str(command_name))


def setup(bot: commands.bot):
    bot.add_cog(Help(bot))
