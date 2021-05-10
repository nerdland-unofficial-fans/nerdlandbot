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
from nerdlandbot.helpers.constants import PETS_DIR_NAME, IMAGE_SIZE, INTERACT_TIMEOUT


class Pets(commands.Cog, name="Pets"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="add_pet",
        brief="add_pet_brief",
        help="add_pet_help",
        usage="add_pet_usage",
    )
    @commands.guild_only()
    async def add_pet(
        self,
        ctx: commands.Context,
        name: typing.Optional[str] = None,
        category: typing.Optional[str] = None,
    ):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )
        if name is None:
            message = translate("pet_need_name", lang)
            return await ctx.send(message)
        if category is None:
            message = translate("pet_need_category", lang)
            return await ctx.send(message)

        if category.lower() not in guild_data.pets_categories:
            message = translate("pet_category_nonexistant", lang)
            return await ctx.send(message)

        
        await guild_data.add_pet(name, ctx.author.id, category.lower())
        pet_id = guild_data.pets_last_id
        if ctx.message.attachments:
            await resize_and_save(ctx, ctx.message.attachments[0], pet_id)
            msg = translate("pet_added_succes", lang).format(
                name.capitalize(), pet_id)
            await ctx.send(msg)
        else:
            embed_title = translate("pet_embed_title", lang)
            question = translate("waiting_question",
                                 lang).format(name.capitalize())
            embed = discord.Embed(
                title=embed_title,
                description=question,
            )
            await ctx.send(embed=embed)
            try:
                reaction = await ctx.bot.wait_for(
                    "message", timeout=INTERACT_TIMEOUT, check=check(ctx.author)
                )

                if reaction.content == "0":
                    await guild_data.delete_pet(pet_id)
                    abort = translate("command_abort", lang)
                    embed = discord.Embed(
                        title=embed_title,
                        description=abort,
                    )
                    return await ctx.send(embed=embed)

                if reaction.attachments:
                    await resize_and_save(ctx, reaction.attachments[0], pet_id)
                    msg = translate("pet_added_succes", lang).format(
                        name.capitalize(), pet_id
                    )
                    await ctx.send(msg)
                else:
                    msg = translate("pet_reaction_error", lang)
                    await ctx.send(msg)

            except asyncio.TimeoutError:
                await guild_data.delete_pet(pet_id)
                timeout = translate("command_timeout", lang)
                embed = discord.Embed(
                    title=embed_title,
                    description=timeout,
                )
                return await ctx.send(embed=embed)

    @commands.command(
        name="post_pet",
        aliases=["pet", "random_pet"],
        brief="post_pet_brief",
        help="post_pet_help",
        usage="post_pet_usage",
    )
    @commands.guild_only()
    async def post_pet(self, ctx: commands.Context, name: typing.Optional[str] = None):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )

        pets = guild_data.pets

        if name == None:
            pet_id = random.choice(list(pets.keys()))
            guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
            filepath = guild_path / f"{pet_id}.jpg"
            message = translate("pet_posted", lang).format(
                pet_id, pets[pet_id]["pet_name"].capitalize(), pets[pet_id]["category"].capitalize()
            )
        elif name in guild_data.pets_categories:
            list_of_ids = list(pets.keys())
            random.shuffle(list_of_ids)
            for pet_id in list_of_ids:
                if pets[pet_id]["category"] == name.lower():
                    guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
                    filepath = guild_path / f"{pet_id}.jpg"
                    message = translate("pet_posted", lang).format(
                        pet_id, pets[pet_id]["pet_name"].capitalize(), name.capitalize()
                    )
                    break
            else:
                message = translate("pet_not_found", lang)
                return await ctx.send(message)
        else:
            list_of_ids = list(pets.keys())
            random.shuffle(list_of_ids)
            for pet_id in list_of_ids:
                if pets[pet_id]["pet_name"] == name.lower():
                    guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
                    filepath = guild_path / f"{pet_id}.jpg"
                    message = translate("pet_posted", lang).format(
                        pet_id, pets[pet_id]["pet_name"].capitalize(), pets[pet_id]["category"].capitalize()
                    )
                    break
            else:
                message = translate("pet_not_found", lang)
                return await ctx.send(message)

        await ctx.send(message)
        await ctx.send(file=discord.File(filepath))

    @commands.command(
        name="remove_pet",
        aliases=["rm_pet"],
        brief="remove_pet_brief",
        usage="remove_pet_usage",
        help="remove_pet_help",
    )
    @commands.guild_only()
    async def remove_pet(
        self, ctx: commands.Context, pet_id: typing.Optional[str] = None
    ):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )

        if pet_id in guild_data.pets:

            if (
                guild_data.user_is_admin(ctx.author)
                or str(ctx.author.id) == guild_data.pets[pet_id]["owner"]
            ):
                await guild_data.delete_pet(pet_id)
                guild_path = Path.cwd() / PETS_DIR_NAME / str(ctx.guild.id)
                filepath = guild_path / f"{pet_id}.jpg"
                filepath.unlink()
                message = translate("pet_removed", lang).format(pet_id)
            else:
                gif = translate("not_admin_gif", lang)
                return await ctx.send(gif)
        else:
            message = translate(
                "pet_picture_does_not_exist", lang).format(pet_id)
        await ctx.send(message)

    @commands.command(
        name="add_category",
        help="pet_add_category_help",
        usage="pet_add_category_usage",
        brief="pet_add_category_brief")
    @commands.guild_only()
    async def add_category(
        self, ctx: commands.Context, category_name: typing.Optional[str] = None
    ):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )
        if category_name is None:
            msg = translate("pet_category_need_name", lang)
            return await ctx.send(msg)

        if guild_data.user_is_admin(ctx.author):
            if await guild_data.add_new_pet_category(category_name.lower()):
                msg = translate("pet_category_succes", lang).format(category_name)
            else:
                msg = translate("pet_category_error", lang)
            return await ctx.send(msg)

        gif = translate("not_admin_gif", lang)
        return await ctx.send(gif)

    @commands.command(
        name="show_categories",
        brief="pet_show_categories_brief",
        help="pet_show_categories_help"  
    )
    @commands.guild_only()
    async def show_categories(self, ctx: commands.Context):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )
        if not guild_data.pets_categories:
            msg = translate("pet_no_categories", lang)
            return await ctx.send(msg)

        msg = translate("pet_categories", lang)
        for category in guild_data.pets_categories:
            msg += f"\n -"
            msg += category.capitalize()

        return await ctx.send(msg)

    @commands.command(
        name="remove_category",
        help="pet_remove_category_help",
        usage="pet_remove_category_usage",
        brief="pet_remove_category_brief"
    )
    @commands.guild_only()
    async def remove_category(self, ctx: commands.Context, category_name: str):
        lang, guild_data = await asyncio.gather(
            culture(ctx),
            get_guild_data(ctx.message.guild.id),
        )
        pets = guild_data.pets

        for pet_id in pets.keys():
            if pets[pet_id]["category"] == category_name.lower():
                msg = translate("pet_category_still_in_use", lang)
                return await ctx.send(msg)

        if category_name is None:
            translation_key = "pet_category_need_name"
        else:
            if await guild_data.remove_pet_category(category_name.lower()):
                translation_key = "pet_category_removal_succes"

        msg = translate(translation_key, lang)
        return await ctx.send(msg)


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
            new_width = img.size[0] / size_deviation ** 0.5
            new_height = new_width / aspect
            # resize from img_orig to not lose quality
            img = img_orig.resize((int(new_width), int(new_height)))


def setup(bot: commands.Bot):
    bot.add_cog(Pets(bot))
