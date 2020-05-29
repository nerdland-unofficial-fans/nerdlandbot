from serverData import loadServerData

async def subscribe(ctx, list_name):
    data = loadServerData(ctx)

    if list_name not in data.notification_lists.keys():
        data.notification_lists[list_name] = []

    if ctx.author.id in data.notification_lists[list_name]:
        await ctx.send('You are already subscribed to this list')
    else:
        data.notification_lists[list_name].append(ctx.author.id)
        await ctx.send('Subscribed ' + ctx.author.nick + ' to ' + list_name)

async def unsubscribe(ctx, list_name):
    data = loadServerData(ctx)

    if list_name not in data.notification_lists.keys():
        await ctx.Send('That list does not seem to exist, cannot unsubscribe')
    else:
        if ctx.author.id in data.notification_lists[list_name]:
            data.notification_lists[list_name].remove(ctx.author.id)
            await ctx.send('Unsubscribed ' + ctx.author.nick + ' from ' + list_name)
        else:
            await ctx.Send('You dont seem to be subscribed to this list')

async def notify(ctx, list_name):
    data = loadServerData(ctx)

    if list_name not in data.notification_lists.keys():
        await ctx.send('That list does not seem to exist')
    else:
        if data.notification_lists[list_name]:
            mentionList = ['<@' + str(id) + '>' for id in data.notification_lists[list_name]]
            await ctx.send('Notifying ' + ', '.join(mentionList))
        else:
            await ctx.send('Nobody to notify')

async def show_lists(ctx):
    data = loadServerData(ctx)

    if data.notification_lists: 
        await ctx.send(', '.join(data.notification_lists.keys()))
    else:
        await ctx.send('No lists exist yet')