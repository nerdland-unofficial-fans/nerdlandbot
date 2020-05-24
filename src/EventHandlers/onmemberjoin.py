import discord 
notification_channel_name = 'botplayground'
member_notification_number = 100


async def on_member_join(bot,member):
  for guild in bot.guilds:
    notification_channel_id = discord.utils.get(guild.channels,name=notification_channel_name).id
    number_members = len(guild.members)
    if number_members%member_notification_number == 0:
      channel = bot.get_channel(notification_channel_id)
      await channel.send('The current member count is {}'.format(number_members))