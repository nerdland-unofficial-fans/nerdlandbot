import typing
import discord
from discord.ext import commands
from mcstatus import MinecraftServer
import dns.resolver

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.helpers.constants import NOTIFY_EMBED_COLOR


class OpenSource(commands.Cog, name="minecraft"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="minecraft", aliases=["mc"], help="minecraft_help",
    )
    @commands.guild_only()
    async def minecraft(
        self, ctx: commands.Context, mention: typing.Optional[str] = None
    ):
        srvInfo = {}
        srv_records = dns.resolver.query("_minecraft._tcp.minecraft.nerdfan.be", "SRV")
        print(str(srv_records))
        for line in srv_records:
            print(str(line.target))

        if len(srv_records) == 0:
            await ctx.send(
                msg=translate("minecraft_server_not_found", await culture(ctx))
            )
            return
        server = MinecraftServer(srv_records[0].target.to_text())
        status = server.status()
        player_names = "\n".join(map(lambda x: f"- {x.name}", status.players.sample))
        s = f"""
        **MOTD:** {status.description}
**Version:** {status.version.name}
**Players:** {status.players.online}/{status.players.max}
{player_names}
        """
        await ctx.send(s)


def setup(bot: commands.Bot):
    bot.add_cog(OpenSource(bot))
