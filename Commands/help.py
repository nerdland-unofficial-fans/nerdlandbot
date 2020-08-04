from discord.ext import commands
import discord

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', usage='\u2000[command or category]',brief='Print the help list', help = 'Print the help list\n\n\u2003[command or category] \u2003 The command or category you need help on')
    async def help(self,ctx,subject=None):
        to_embed = discord.Embed()
        
        if subject == None:
            for cog_name in ctx.bot.cogs:
                msg=[] 
                message = {}   
                cog = ctx.bot.get_cog(cog_name)
                for command in cog.get_commands():
                    if not command.hidden:  
                        if command.brief == None:
                            message[command.name] = command.help
                            msg.append("*{0}*\n \u2003 {1}\n".format(command.name,command.help))
                        else:
                            message[command.name] = command.brief
                            msg.append("*{0}*\n \u2003 {1}\n".format(command.name,command.brief))
                string = []
                if cog_name == 'converters':
                    for name in message.keys():
                        string.append("__*{0}*__\n \u2003 {1}\n".format(name,message[name]))
                else:
                    for name in sorted(message):
                        string.append("__*{0}*__\n \u2003 {1}\n".format(name,message[name]))

                to_embed.add_field(name='~~-'+' '*30+'-~~' + '\n**' + cog_name + '**\n', value=" ".join(string), inline=False)
            to_embed.add_field(name='\u200b', value="Type `{0}help [command]` for more info on a command. \nType `{0}help [category]` for more info on a category.".format(ctx.prefix), inline=False)
        else:
            for cog_name in ctx.bot.cogs:
                if cog_name == subject:
                    cog = ctx.bot.get_cog(cog_name)
                    to_embed = discord.Embed()
                    msg=[]
                    message={}
                    for command in cog.get_commands():
                        if not command.hidden:  
                            if command.brief == None:
                                message[command.name] = command.help
                            else:
                                message[command.name] = command.brief
                    string = []
                    if cog_name == 'converters':
                        for name in message.keys():
                            string.append("__*{0}*__\n \u2003 {1}\n".format(name,message[name]))
                    else:
                        for name in sorted(message):
                            string.append("__*{0}*__\n \u2003 {1}\n".format(name,message[name]))

                    to_embed.add_field(name= '**'+cog_name + '**\n', value=" ".join(string), inline=False)
                    to_embed.add_field(name='\u200b', value="Type `{0}help [command]` for more info on a command.".format(ctx.prefix), inline=False)
            # to_embed.add_field(name='\u200b', value="Arguments with <> are required.\nArguments with [] are optional.", inline=False)

            for command_name in ctx.bot.commands:
                if str(command_name) == str(subject):
                    command = ctx.bot.get_command(str(command_name))
                    to_embed = discord.Embed()
                    msg=[]
                    if command.usage == None:
                        to_embed.add_field(name=ctx.prefix+command.name+'\n', value=command.help, inline=False)
                    else:
                        to_embed.add_field(name=ctx.prefix+command.name+'\u2000'+command.usage+'\n', value=command.help, inline=False)
                        to_embed.add_field(name='\u200b', value="Arguments with <> are required.\nArguments with [] are optional.", inline=False)
            
        if len(to_embed) == 0: 
            to_embed.add_field(name='\u200b', value="The argument you gave is not a category or command. Use {0} without an argument to get all the categories and commands.".format(ctx.prefix), inline=False)
            
        await ctx.channel.send(embed = to_embed)
def setup(bot):
    bot.add_cog(Help(bot))