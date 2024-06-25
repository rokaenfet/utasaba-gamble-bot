import discord
import time
import logging
from discord.ext import commands
# from pretty_help import PrettyHelp

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
VOICE_CHANNEL_ID = 1253358975663997009

# VOICE CHANNEL ACTIVITY LIST
user_join_times = dict()
user_total_times = dict()

# LOGGING
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# LOAD TOKEN KEY
DISCORD_TOKEN = load_bot_token()

# VERBOSITY
VERBOSE = True

intents = discord.Intents.all()
# menu = PrettyHelp()
bot = commands.Bot(command_prefix = ["!","/","?","fish "], intents=intents, case_insensitive=True)

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
        await bot.process_commands(msg)

# reward for time spent in voice channel check
@bot.event
async def on_voice_state_update(member:discord.Member, before:discord.VoiceState, after:discord.VoiceState):
    # The specific channel ID you want to track
    specific_channel_id = VOICE_CHANNEL_ID  # Replace with your channel ID
    time_spent = None

    # User joins the specific voice channel
    if before.channel is None and after.channel and after.channel.id == specific_channel_id:
        user_join_times[member.id] = datetime.datetime.now(datetime.timezone.utc)
        print(f'{member} joined {after.channel.name} at {user_join_times[member.id]}')

    # User leaves the specific voice channel
    elif before.channel and before.channel.id == specific_channel_id and (after.channel is None or after.channel.id != specific_channel_id):
        join_time = user_join_times.pop(member.id, None)
        if join_time:
            time_spent = datetime.datetime.now(datetime.timezone.utc) - join_time
            if member.id in user_total_times:
                user_total_times[member.id] += time_spent
            else:
                user_total_times[member.id] = time_spent
            print(f'{member} left {before.channel.name} after {time_spent}')
            print(f'Total time spent by {member}: {user_total_times[member.id]}')

    # User switches between channels and one of them is the specific channel
    elif before.channel and after.channel and before.channel.id != after.channel.id:
        if before.channel.id == specific_channel_id:
            join_time = user_join_times.pop(member.id, None)
            if join_time:
                time_spent = datetime.utcnow() - join_time
                if member.id in user_total_times:
                    user_total_times[member.id] += time_spent
                else:
                    user_total_times[member.id] = time_spent
                print(f'{member} left {before.channel.name} after {time_spent}')
                print(f'Total time spent by {member}: {user_total_times[member.id]}')

        if after.channel.id == specific_channel_id:
            user_join_times[member.id] = datetime.datetime.now(datetime.timezone.utc)
            print(f'{member} joined {after.channel.name} at {user_join_times[member.id]}')

    # if time has been spent in vc
    if time_spent:
        # reward by time spent in vc
        await update_bal_delta(round(time_spent.total_seconds()*10,-2), member.name)

# COMMAND
@bot.command(name="sync")
@commands.has_role("Admin")
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