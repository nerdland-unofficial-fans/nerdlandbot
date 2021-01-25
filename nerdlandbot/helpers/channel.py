import discord

def get_channel(ctx, channel_input:str): 
    """
    Returns a channel object based on an id or a name.
    :param channel_input: The input string to parse to a channel name. (str)
    :return: The channel object. (str)
    """
    if channel_input[:2] == '<#':
        channel = ctx.bot.get_channel(int(channel_input[2:-1]))
    elif channel_input.isnumeric():
        channel = ctx.bot.get_channel(int(channel_input))
    else: 
        channel = discord.utils.get(ctx.channel.guild.channels, name=channel_input)
        
    return channel