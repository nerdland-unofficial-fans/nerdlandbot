import typing
import discord
from discord.ext import commands
import asyncio
import random
from PIL import Image 
import io
from pathlib import Path

from nerdlandbot.translations.Translations import get_text as translate
from nerdlandbot.helpers.TranslationHelper import get_culture_from_context as culture
from nerdlandbot.commands.GuildData import get_guild_data, GuildData
from nerdlandbot.helpers.constants import PETS_DIR_NAME, IMAGE_SIZE

class Pets(commands.Cog, name="Pets"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @commands.command(name="add_pet")
    @commands.guild_only()
    async def add_pet(self, ctx:commands.Context, name:typing.Optional[str] = None):
        lang = await culture(ctx)
        guild_data = await get_guild_data(ctx.message.guild.id)

        pet_id = await guild_data.set_pet(name, str(ctx.author.id))
        if ctx.message.attachments:
            await resize_and_save(ctx,ctx.message.attachments[0],pet_id)
            msg = "Pet {0} added as number {1}!".format(name.capitalize(), pet_id)
            await ctx.send(msg)
        else:
            embed_title = 'Voeg een foto toe'
            question = 'Reageer hierop met de foto van {0} die je wil toevoegen. \n Reageer met 0 om te annuleren'.format(name.capitalize())
            embed = discord.Embed(
                title = embed_title,
                description = question,
            )
            await ctx.send(embed=embed)
            try:
                reaction = await ctx.bot.wait_for("message", timeout=30, check=check(ctx.author))
    
                if reaction.content == "0":
                    await guild_data.delete_pet(pet_id)
                    abort = translate("recipe_abort", lang)
                    embed = discord.Embed(
                        title = embed_title,
                        description = abort,
                    )
                    return await ctx.send(embed=embed)
                    

                if reaction.attachments:
                    await resize_and_save(ctx,reaction.attachments[0],pet_id)
                else: 
                    msg = 'Voeg een foto toe, foemp!'
                    await ctx.send(msg)
                
            except asyncio.TimeoutError:
                timeout = translate("recipe_timeout", lang)
                embed = discord.Embed(
                    title = embed_title,
                    description = timeout,
                )
                return await ctx.send(embed=embed)
        
    @commands.command(name="post_pet")
    @commands.guild_only()
    async def post_pet(self, ctx:commands.Context, name:typing.Optional[str] = None):
        lang = await culture(ctx)
        guild_data = await get_guild_data(ctx.message.guild.id)

        pets = guild_data.pets

        if name == None:
            pet_id = random.choice(list(pets.keys()))
            guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
            filepath = guild_path / f"{pet_id}.jpg"
            message = "Dit is foto {0} van {1}".format(pet_id, pets[pet_id]['pet_name'].capitalize())
        else:
            list_of_ids = list(pets.keys())
            random.shuffle(list_of_ids)
            pet_found = False
            for pet_id in list_of_ids:
                if pets[pet_id]['pet_name'] == name.lower() and not pet_found:
                    guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
                    filepath = guild_path / f"{pet_id}.jpg"
                    message = "Dit is foto {0} van {1}".format(pet_id, pets[pet_id]['pet_name'].capitalize())
                    pet_found = True

            if not pet_found:
                message = "Er is geen dier gevonden met die naam."
                return await ctx.send(message)

        await ctx.send(message)
        await ctx.send(file=discord.File(filepath))

    @commands.command(name="remove_pet")
    @commands.guild_only()
    async def remove_pet(self, ctx:commands.Context, pet_id:typing.Optional[str] = None):
        lang = await culture(ctx)
        guild_data = await get_guild_data(ctx.message.guild.id)

        if pet_id in guild_data.pets:

            if guild_data.user_is_admin(ctx.author) or str(ctx.author.id) is guild_data.pets[pet_id]["owner"]:
                await guild_data.delete_pet(pet_id)
                guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
                filepath = guild_path / f"{pet_id}.jpg"
                filepath.unlink()
                message = "Picture {0} removed from data".format(pet_id)
            else: 
                gif = translate("not_admin_gif", lang)
                return await ctx.send(gif)
        else:
            message = "Picture {0} doesn't exist".format(pet_id)
        await ctx.send(message)
        

async def resize_and_save(ctx, attachment, pet_id):
    guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
    guild_path.mkdir(exist_ok=True, parents=True)
    
    old_path = guild_path / f"{pet_id}_old.jpg"
    new_path = guild_path / f"{pet_id}.jpg"

    await attachment.save(str(old_path))
    limit_img_size(old_path, new_path, IMAGE_SIZE, tolerance=5)
    old_path.unlink()


def check(author):
    def inner_check(message):
        return message.author == author
    return inner_check


def limit_img_size(img_filename, img_target_filename, target_filesize, tolerance=5):
    img = img_orig = Image.open(img_filename)
    aspect = img.size[0] / img.size[1]

    while True:
        with io.BytesIO() as buffer:
            img.save(buffer, format="JPEG")
            data = buffer.getvalue()
        filesize = len(data)    
        size_deviation = filesize / target_filesize

        if size_deviation <= (100 + tolerance) / 100:
            # filesize fits
            with open(img_target_filename, "wb") as f:
                f.write(data)
            break
        else:
            # filesize not good enough => adapt width and height
            # use sqrt of deviation since applied both in width and height
            new_width = img.size[0] / size_deviation**0.5    
            new_height = new_width / aspect
            # resize from img_orig to not lose quality
            img = img_orig.resize((int(new_width), int(new_height)))

def setup(bot: commands.Bot):
    bot.add_cog(Pets(bot))