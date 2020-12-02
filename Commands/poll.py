import discord
import typing
import asyncio
import time

from discord.ext import commands
from Translations.Translations import get_text as translate
from Helpers.TranslationHelper import get_culture_from_context as culture
from Helpers.TranslationHelper import get_culture_from_context as get_culture_from_context
from Helpers.emoji import number_emojis, yes, no, drum
from Helpers.constants import POLL_MAX_TIMEOUT

class Poll(commands.Cog, name="Simple Poll"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="poll", brief="poll_brief", usage="poll_usage", help="poll_help")
    async def poll(self, ctx: commands.Context, *, input_str: str):
        """
        Create a poll with either yes or no asn an answer of self submitted options.
        Poll will be open for an amount of time determined by the user.

        Syntax: question (multiple words) timeout (numerals) <options> (words split by ;)
        Example: This is a quention? 10 option 1; option 2; option 3

        :param input: input to be parsed according to above syntax
        """

        poller_id = ctx.message.author.id

        #check if there is a question
        if '?' not in input_str:
            await ctx.send(translate("poll_no_questionmark", await culture(ctx)))
            return

        input_split = input_str.split('?',1)
        question = input_split[0]
        numbers_and_options = input_split[1].strip()
        
        # parse timeout
        numbers = [int(s) for s in numbers_and_options.split() if s.isdigit()]
        if len(numbers) < 1:
            await ctx.send(translate("poll_no_timeout", await culture(ctx)))
            return
        timeout_s = int(numbers[0]) * 60
        if timeout_s > POLL_MAX_TIMEOUT:
            await ctx.send(translate("poll_max_timeout", await culture(ctx)))
            return

        # parse options
        options = numbers_and_options.split(str(numbers[0]),1)[1].strip()
        if len(options) > 0:
            options = options.split(';')
            is_yes_no = False
        else:
            is_yes_no = True
        
        # create message to send to channel
        txt = translate("poll_start", await culture(ctx)).format(poller_id,question)

        # add options to message
        options_dict = dict()
        if is_yes_no:
            txt += translate("poll_yes_no", await culture(ctx)).format(yes,no)
            options_dict[yes] = translate("yes", await culture(ctx))
            options_dict[no] = translate("no", await culture(ctx))
        else:
            i = 1
            for option in options:
                txt += "{} - {}\n".format(number_emojis[i],option)
                options_dict[number_emojis[i]] = option
                i += 1
        
        msg = await ctx.send(txt)

        # add reactions to message
        if is_yes_no:
            await msg.add_reaction(yes)
            await msg.add_reaction(no)
        else:
            i = 1
            for option in options:
                await msg.add_reaction(number_emojis[i])
                i += 1

        # wait until timeout
        await asyncio.sleep(timeout_s)

        # refresh message
        msg = await ctx.fetch_message(msg.id)
        
        # get the reactions
        reactions = msg.reactions
        reactions_dict = dict()
        for reaction in reactions:
            reactions_dict[reaction.emoji] = reaction.count
        reactions_sorted = sorted(reactions_dict.items(), key=lambda x: x[1], reverse=True)

        # send poll results
        txt = translate("poll_results", await culture(ctx)).format(drum,poller_id,question)
        for reaction in reactions_sorted:
            try:
                option_str = options_dict[reaction[0]].strip()
                count = reaction[1] - 1
                txt += translate("poll_votes", await culture(ctx)).format(option_str,count)
                pass
            except:
                pass

        # send message with results
        await ctx.send(txt)

def setup(bot: commands.bot):
    bot.add_cog(Poll(bot))