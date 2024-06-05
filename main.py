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
TEXT_CHANNEL_ID = 1247839269125488650

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

    # SHIRITORI
    # load specified text_channel's history
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)
    # order from oldest = [0], newest = [-1]
    t = time.time()
    messages = [message async for message in text_channel.history(limit=None)]
    if len(messages) == 0:
        await text_channel.send(f"しりとり")
        update_json("shiritori", {"last_message":"しりとり", "user":bot.user.name})
    else:
        # check for last message which doesn't end in ん and is all japanese
        special_chars = ["!",",",".","。","?"]
        for msg in messages:
            msg_str = msg.content
            # strip special chars
            for specials in special_chars:
                msg_str = msg_str.replace(specials,"")
            jp_chars = await find_japanese_from_str(msg_str)
            if len(jp_chars) > 0 and len(jp_chars) == len(msg_str) and msg_str[-1] != "ん":
                break
        update_json("shiritori", {"last_message":msg_str, "user":msg.author.name})
    temp = await read_json("shiritori")
    print(f"loaded all msg in #{text_channel}. Load time: {round(time.time()-t,3)}s")

# on message send in specific channel
@bot.event
async def on_message(msg:discord.Message):
    # only activate on designated text channel id
    if msg.channel.id == TEXT_CHANNEL_ID and msg.author.name != bot.user.name:
        shiritori_data = await read_json("shiritori")
        last_word = shiritori_data["last_message"]
        cur_msg_content = msg.content
        if cur_msg_content[-1] != "ん":
            if cur_msg_content[0] == last_word[-1]:
                update_json("shiritori",{"last_message":cur_msg_content,"user":msg.author.name})
                await update_bal_delta(100, msg.author.name)
                await msg.add_reaction(str("✅"))
            else:
                await msg.add_reaction(str("❌"))
                await msg.channel.send(f"現在の言葉は`{shiritori_data['last_message']}`です:exclamation:")
        else:
            await msg.add_reaction(str("🆖"))
            await msg.channel.send(f"現在の言葉は`{shiritori_data['last_message']}`です:exclamation:")
            
    # if command is else where, proceed
    elif msg.channel.id != TEXT_CHANNEL_ID:
        await bot.process_commands(msg)


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