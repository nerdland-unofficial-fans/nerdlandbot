from .serverData import load_guild_config, save_configs

async def subscribe(ctx, list_name):    
    config = await load_guild_config(ctx)

    if list_name not in config.notification_lists.keys():
        config.notification_lists[list_name] = []

    if ctx.author.id in config.notification_lists[list_name]:
        await ctx.send('You are already subscribed to this list')
    else:
        config.notification_lists[list_name].append(ctx.author.id)
        config.guild_changed = True

        await ctx.send('Subscribed ' + ctx.author.nick + ' to ' + list_name)

async def unsubscribe(ctx, list_name):
    config = await load_guild_config(ctx)

    if list_name not in config.notification_lists.keys():
        await ctx.Send('That list does not seem to exist, cannot unsubscribe')
    else:
        if ctx.author.id in config.notification_lists[list_name]:
            config.notification_lists[list_name].remove(ctx.author.id)
            config.guild_changed = True
        
            await ctx.send('Unsubscribed ' + ctx.author.nick + ' from ' + list_name)
        else:
            await ctx.Send('You dont seem to be subscribed to this list')

async def notify(ctx, list_name):
    config = await load_guild_config(ctx)

    if list_name not in config.notification_lists.keys():
        await ctx.send('That list does not seem to exist')
    else:
        if config.notification_lists[list_name]:
            mentionList = ['<@' + str(id) + '>' for id in config.notification_lists[list_name]]
            await ctx.send('Notifying ' + ', '.join(mentionList))
        else:
            await ctx.send('Nobody to notify')

async def show_lists(ctx):
    config = await load_guild_config(ctx)

    if config.notification_lists:
        await ctx.send(', '.join(config.notification_lists.keys()))
    else:
        await ctx.send('No lists exist yet')

async def save_config(ctx):
    await save_configs(ctx)
    await ctx.send('Configurations saved')