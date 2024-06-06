import os
import discord
import asyncio
import time
import logging
import schedule
import re
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

from funcs import *

async def load_extensions():
    for ext in get_extensions():
        await bot.load_extension(f"cogs.{ext}")
        print(f"Loaded extension cogs.{ext}")

# CHANNEL ID
SHIRITORI_CHANNEL_ID = 1247839269125488650
MESHITERO_CHANNEL_ID = 1248150136656232479
DOUBUTSU_CHANNEL_ID = 1248150177743896607
ALL_SPECIAL_CHANNEL_ID = [
    SHIRITORI_CHANNEL_ID,
    MESHITERO_CHANNEL_ID,
    DOUBUTSU_CHANNEL_ID
    ]

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

# EVENTT
# on ready
@bot.event
async def on_ready():
    # LOAD COGS / EXTENSIONS
    await load_extensions()

    # CONFIRM LOGIN
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # SHIRITORI INIT
    await shiritori_on_ready(bot=bot, TEXT_CHANNEL_ID=SHIRITORI_CHANNEL_ID)

# on message send in specific channel
@bot.event
async def on_message(msg:discord.Message):
    # only activate on designated text channel id
    if msg.channel.id == SHIRITORI_CHANNEL_ID and msg.author.name != bot.user.name:
        await shiritori_on_message(msg=msg)

    # doubutsu & meshitero img
    if msg.channel.id in (DOUBUTSU_CHANNEL_ID, MESHITERO_CHANNEL_ID) and msg.author.name != bot.user.name:
        await on_message_image_upload_daily(msg=msg)
            
    # if command is else where, proceed
    elif msg.channel.id not in ALL_SPECIAL_CHANNEL_ID:
        await bot.process_commands(msg=msg)


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

main()