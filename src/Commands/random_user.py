import random

async def choose(bot, ctx, channel=None):

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

        user = random.choice(array)
        await ctx.send(f'Ik heb <@{user.id}> gekozen!')


    elif channel is not None:
        kanaal = discord.utils.get(ctx.channel.guild.channels, name=channel)

        if kanaal is None:
            return await ctx.send("Geef een correct kanaal mee!")
        if len(kanaal.members) < 1:
            return await ctx.send("In dat kanaal zijn geen members!")
        user = random.choice(kanaal.members)
        await ctx.send(f'Ik heb <@{user.id}> gekozen!')
        print(len(kanaal.members))
    else:
        await ctx.send("Geef een kanaalnaam mee")