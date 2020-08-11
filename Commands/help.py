from discord.ext import commands
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture

import discord

empty = '\u200b'


def build_title(title: str) -> str:
    return f"~~-{' ' * 30}-~~" + '\n' + f"**{title}**" + '\n'


async def send_embed(ctx: commands.context, embed: discord.Embed):
    if len(embed) > 0:
        return await ctx.channel.send(embed=embed)

    # if we reach here, the embed is empty and we show an error
    name = empty
    value = translate("help_err_not_recognized", await culture(ctx)).format(ctx.prefix)
    embed.add_field(name=name, value=value, inline=False)
    await ctx.channel.send(ctx, embed)


async def build_commands_message(ctx: commands.Context, cog_name: str) -> str:
    cog = ctx.bot.get_cog(cog_name)

    message = {}
    for command in cog.get_commands():
        if command.hidden:
            continue

        if command.brief is None:
            message[command.name] = translate(command.help, await culture(ctx))
        else:
            message[command.name] = translate(command.brief, await culture(ctx))

    strings = []
    for name in sorted(message):
        strings.append("*{0}*\n \u2003 {1}\n".format(name, message[name]))

    return ' '.join(strings)


async def general_help(ctx: commands.Context):
    embed = discord.Embed()

    for cog_name in ctx.bot.cogs:
        content = await build_commands_message(ctx, cog_name)

        if len(content) == 0:
            continue

        title = build_title(cog_name)
        embed.add_field(name=title, value=content, inline=False)

    extra_info_command = translate("help_info_command", await culture(ctx)).format(ctx.prefix)
    extra_info_category = translate("help_info_category", await culture(ctx)).format(ctx.prefix)
    extra_info = f'{extra_info_command}\n{extra_info_category}'
    embed.add_field(name=empty, value=extra_info, inline=False)
    await send_embed(ctx, embed)


async def subject_help(ctx: commands.Context, subject: str):
    embed = discord.Embed()
    content = await build_commands_message(ctx, subject)

    # add subject title
    title = f'**{0}**\n'.format(subject)
    embed.add_field(name=title, value=content, inline=False)

    # add extra info
    extra_info = translate("help_info_command", await culture(ctx)).format(ctx.prefix)
    embed.add_field(name=empty, value=extra_info, inline=False)

    await send_embed(ctx, embed)


async def command_help(ctx: commands.Context, command_name: str):
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
        if subject is None:
            return await general_help(ctx)

        for cog_name in ctx.bot.cogs:
            if cog_name.lower() == subject.lower():
                return await subject_help(ctx, cog_name)

        for command_name in ctx.bot.commands:
            if str(command_name) == str(subject):
                return await subject_help(ctx, command_name)


def setup(bot: commands.bot):
    bot.add_cog(Help(bot))
