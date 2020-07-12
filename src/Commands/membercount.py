import random
import discord

async def count(bot, ctx, channel=None):

    if channel == "online":
        
        def myFunc(x):
            if str(x.status) == "online" or str(x.status) == "dnd":
                return True
            else:
                return False

        onlineMembers = filter(myFunc, ctx.guild.members)
        array = []
        for x in onlineMembers:
            array.append(x)

        await ctx.send(f'In deze server zijn {len(array)} mensen online!')

    elif channel is not None:
        kanaal = discord.utils.get(ctx.channel.guild.channels, name=channel)

        if kanaal is None:
            return await ctx.send("Geef een correcte kanaalnaam mee!")
        if len(kanaal.members) < 1:
            return await ctx.send("In dat kanaal zitten geen members!")
        elif len(kanaal.members) == 1:
            await ctx.send(f'In het kanaal <#{kanaal.id}> zit {len(kanaal.members)} persoon!')
        else:
            await ctx.send(f'In het kanaal <#{kanaal.id}> zitten {len(kanaal.members)} mensen!')

    else:
       await ctx.send(f'In `{ctx.guild.name}` zitten {len(ctx.guild.members)} mensen!')
