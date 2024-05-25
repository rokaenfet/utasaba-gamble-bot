import os
import discord
import json
import asyncio
import sys
import random
from discord.ext import commands
from dotenv import load_dotenv

def read_json(json_name):
    f = open(f"json/{json_name}.json")
    data = json.load(f)
    f.close()
    return data

def update_json(json_name,dict):
    with open(f"json/{json_name}.json",mode="w") as f:
        json.dump(dict, f, indent=6, skipkeys=True)

def check_is_num(txt):
    try:
        val = int(txt)
        return True
    except:
        return False

# CHECK MID-GAME
midgame_rps_users = set()

# EXTERNAL FILES
gamble_data = read_json("gamble")

# LOAD TOKEN KEY
load_dotenv("token.env")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")


# CONNECT BOT
intents = discord.Intents.all()

# COMMAND PREFIX
bot = commands.Bot(command_prefix = "!", intents=intents, case_insensitive=True)

# EVENTS
@bot.event
async def on_ready():
    # confirm login
    print(f'We have logged in as {bot.user}')

# COMMANDS
@bot.command()
async def info(ctx):
    """
    !info
    guild
    author
    message.id
    """
    await ctx.reply(f"guild: {ctx.guild}\nauthor: {ctx.author}\nsender: {ctx.message.id}")

@bot.command()
async def bal(ctx):
    """
    !bal
    get your bal / make new bank account if non-existing
    """
    user_name = ctx.author.name
    if user_name in gamble_data:
        await ctx.reply(f"{user_name}さんの残高: {gamble_data[user_name]}")
    else:
        await ctx.reply(f"**{ctx.author.nick}**様の新しい口座が設立されました")
        gamble_data[user_name] =  0
    await update_json("gamble", gamble_data)

@bot.command()
async def ask_for_num_input(ctx):
    await ctx.send("いくら賭ける？")
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and check_is_num(msg.content)
    try:
        msg = await bot.wait_for("message", check=check, timeout=10)
        
    except asyncio.TimeoutError:
        await ctx.send("返信が（判断が）遅い！")
        return False
    return int(msg)

@bot.command(aliases = ["rock-paper-scissors, じゃんけん"])
async def rps(ctx):
    # ask how much they want to bet
    bet_amount = ask_for_num_input()

    # register user as midgame
    player_id = ctx.message.author.id
    if player_id not in midgame_rps_users:
        midgame_rps_users.add(player_id)
    else:
        await ctx.send("もうじゃんけんしてるよ！早く手を出して！")
        return
    rps_dict = {
        "ぐー":0,
        "ちょき":1,
        "ぱー":2
    }
    def check(msg):
        return msg.content in rps_dict and msg.author == ctx.author and msg.channel == ctx.channel
    rps_first_round = True
    winner = None
    while winner is None:
        if rps_first_round:
            await ctx.send("「ぐー」「ちょき」「ぱー」で返信してね！\n最初はグ～、じゃんけん...")
        else:
            await ctx.send("あいこでグ～、じゃんけん...")
        try:
            res = await bot.wait_for("message", check=check, timeout=10.0)
            player_hand = res.content
            rps_first_round = False
            bot_hand = random.choice(["ぐー","ちょき","ぱー"])
            await ctx.send(f"{bot_hand}!")
            player_hand_num, bot_hand_num = rps_dict[player_hand], rps_dict[bot_hand]
            # check game end
            if (player_hand_num+1)%3 == bot_hand_num:
                winner = "player"
            elif (bot_hand_num+1)%3 == player_hand_num:
                winner = "bot"
        except asyncio.TimeoutError:
            await ctx.send("遅い！最初から！")
            return
    if winner is not None:
        if winner == "player":
            await ctx.send("ま、負けた、、、")
        else:
            await ctx.send("勝った！gg~")

    
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    pass

# MAIN | RUN BOT
async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

# RUN MAIN
asyncio.run(main())