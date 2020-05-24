notification_lists = dict()

async def subscribe(ctx, list_name):
    if list_name not in notification_lists.keys():
        notification_lists[list_name] = []

    if ctx.author.id in notification_lists[list_name]:
        await ctx.send('You are already subscribed to this list')
    else:
        notification_lists[list_name].append(ctx.author.id)
        await ctx.send('Subscribed ' + ctx.author.nick + ' to ' + list_name)

async def unsubscribe(ctx, list_name):
    if list_name not in notification_lists.keys():
        await ctx.Send('That list does not seem to exist, cannot unsubscribe')
    else:
        if ctx.author.id in notification_lists[list_name]:
            notification_lists[list_name].remove(ctx.author.id)
            await ctx.send('Unsubscribed ' + ctx.author.nick + ' from ' + list_name)
        else:
            await ctx.Send('You dont seem to be subscribed to this list')

async def notify(ctx, list_name):
    if list_name not in notification_lists.keys():
        await ctx.send('That list does not seem to exist')
    else:
        if notification_lists[list_name]:
            mentionList = ['<@' + str(id) + '>' for id in notification_lists[list_name]]
            await ctx.send('Notifying ' + ', '.join(mentionList))
        else:
            await ctx.send('Nobody to notify')

async def show_lists(ctx):
    if notification_lists: 
        await ctx.send(', '.join(notification_lists.keys()))
    else:
        await ctx.send('No lists exist yet')    