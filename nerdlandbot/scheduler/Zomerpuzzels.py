import asyncio
import json
import os

from datetime import datetime, timedelta
from discord.ext import tasks

from nerdlandbot.commands.notify import notify

initialized = False

@tasks.loop(seconds=1.0)
async def post_puzzle(bot):
    info("Running post_puzzle")
    current_time = datetime.now()

    if initialized:
        with open(os.path.join('zomerpuzzels', 'puzzles.json'), 'r') as puzzles_file:
            puzzles = json.load(puzzles_file)

        assets_path = os.path.join('zomerpuzzels', 'assets')

        puzzle_images = sort([f for f in os.listdir(assets_path) if os.path.isfile(os.path.join(assets_path, f)) and f[:4] == ".jpg"])

        date_string = current_time.isoformat()

        try:
            puzzle_index = puzzle_images.index(date_string + ".jpg")
        except ValueError as e:
            return error("puzzle index not found")

        if puzzle_index not in puzzles:
            return error("puzzle index not in json")

        if puzzle_index > 1:
            prev_puzzle = puzzle[puzzle_index - 1]
        else:
            prev_puzzle = None

        msg = "!notify Zomerpuzzel\n\n"

        if prev_puzzle:
            msg += f"Antwoord van Puzzel #{puzzle_index}: ||{prev_puzzle}||\n\n"

        msg += f"Puzzel #{puzzle_index + 1}:"

        info("Posting puzzle")
        channel_id = guild_data.puzzle_channel
        channel = bot.get_channel(channel_id)

        await notify()

    delta_hours = 23 - current_time.hours
    delta_minutes = 59 - current_time.minutes
    delta_seconds = 59 - current_time.seconds
    change_interval(hours=delta_hours, minutes=delta_minutes, seconds=delta_seconds)
