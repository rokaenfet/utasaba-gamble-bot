import os
import discord
import json
import asyncio
import sys
import random
import time
import logging
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

from funcs import *

async def load_extensions():
    for ext in get_extensions():
        await bot.load_extension(f"cogs.{ext}")
        print(f"Loaded extension cogs.{ext}")

# LOGGING
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# CHECK MID-GAME
midgame_rps_users = set()
midbet_users = set()

# EXTERNAL FILES
gamble_data = read_json("gamble")

# LOAD TOKEN KEY
load_dotenv("token.env")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

# VERBOSITY
VERBOSE = True

intents = discord.Intents.all()
menu = PrettyHelp()
bot = commands.Bot(command_prefix = ["!","/","?","fish "], intents=intents, case_insensitive=True, help_command=menu)

# EVENTS
@bot.event
async def on_ready():
    # load extensions
    await load_extensions()
    # confirm login
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

# COMMAND
@bot.command(name="sync")
@commands.is_owner()
async def sync(ctx):
    print("SYNCING")
    sync_timer = time.time()
    # sync cog to guild
    guild_id = get_guild_id()
    success_embed = discord.Embed(title=f"Synced **success** :white_check_mark:", description=f"synced with guild id {guild_id}, {bot.get_guild(guild_id)}", color=discord.Color.brand_green())
    try:
        await bot.tree.sync(guild=discord.Object(guild_id))
        print("SYNCED")
        await ctx.reply(embed=success_embed)
    except Exception as e:
        print("SYNC FAILED")
        fail_embed = discord.Embed(title=f"Sync **failed** :x:", description=f"ERROR = {e}",color=discord.Color.brand_red())
        await ctx.reply(embed=fail_embed)      
    print(f"process completed in {round(number=time.time()-sync_timer, ndigits=3)}s")  

# MAIN
def main():
    bot.run(token=DISCORD_TOKEN, log_handler=handler)
    # async with bot:
    #     await bot.start(DISCORD_TOKEN, log_handler=handler)

# bot.start MAIN
# async def main():
#     async with bot:
#         await bot.start(DISCORD_TOKEN, log_handler=handler)
# asyncio.run(main)