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

def update_json(json_name, dict):
    with open(f"json/{json_name}.json",mode="w") as f:
        json.dump(dict, f, indent=6, skipkeys=True)

def check_is_num(txt):
    try:
        val = int(txt)
        return True
    except:
        return False
    
def update_bal(amount, user_name):
    """
    amount [int]
    user_name = str [ctx.author.name]
    """
    gamble_data = read_json("gamble")
    gamble_data[user_name] = amount
    update_json("gamble", gamble_data)

# GAMBLE RATES
GAMBLE_RATES = {
    "rps":3
}

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
    gamble_data = read_json("gamble")
    """
    !bal
    get your bal / make new bank account if non-existing
    """
    user_name = ctx.author.name
    if user_name in gamble_data:
        await ctx.reply(f"{user_name}の残高: {gamble_data[user_name]}")
    else:
        await ctx.reply(f"**{ctx.author.nick}**様の新しい口座が設立されました")
        gamble_data[user_name] =  0
    await update_json("gamble")

@bot.command()
async def ask_for_num_input(ctx):
    gamble_data = read_json("gamble")
    # register and check user is midbet
    player_id = ctx.message.author.id
    if player_id not in midbet_users:
        midbet_users.add(player_id)
    else:
        midbet_users.remove(player_id)
        return False
    # user in question
    user = ctx.author.name
    # ask how much to bet
    await ctx.reply("いくら賭ける？")
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    try:
        # wait for res
        res = await bot.wait_for("message", check=check, timeout=5)
        msg = res.content
        # check for all-ins
        if msg.lower() in ("all","オール","オールイン","おーる","おーるいん"):
            await ctx.reply(f"{gamble_data[user]},全財産オールインだ！")
            midbet_users.remove(player_id)
            update_bal(0, user)
            return gamble_data[user]
        # check inp is an int
        if check_is_num(msg):
            midbet_users.remove(player_id)
            num = int(msg)
            # check user has the amount of money
            if num > gamble_data[user]:
                await ctx.reply("体でも売るつもりかい？そんな金君持ってないよ？")
                return False
            # check user has entered a positive int
            elif num <= 0:
                await ctx.reply("０以下はだぁめぇだねぇ~")
                return False
            # if all condition passed, return num
            else:
                await ctx.reply(f"{num} ベットぉ！")
                update_bal(gamble_data[user]-num, user)
                return num
        # catch non-int (float inc)
        else:
            await ctx.reply("数字を入れてください...")
            midbet_users.remove(player_id)
            return False
    # response timeout
    except asyncio.TimeoutError:
        await ctx.reply("判断が（返信が）遅い！")
        midbet_users.remove(player_id)
        return False

@bot.command(aliases = ["rock-paper-scissors, じゃんけん"])
async def rps(ctx):
    # user in question
    user = ctx.author.name
    # ask how much they want to bet
    bet_amount = await ctx.invoke(bot.get_command("ask_for_num_input"))
    if not bet_amount:
        return
    if VERBOSE: await ctx.send(f"LOG: bet amount = {bet_amount}, game = rps")
    # register and check user is mid-game
    if VERBOSE: await ctx.send(f"current users: {midgame_rps_users}")
    player_id = ctx.message.author.id
    if player_id not in midgame_rps_users:
        midgame_rps_users.add(player_id)
    else:
        await ctx.reply("もうじゃんけんしてるよ！早く手を出して！")
        return
    # load rps
    if VERBOSE: await ctx.send(f"LOG load rps with user: {user}")
    rps_dict = {
        "ぐー":0,
        "ちょき":1,
        "ぱー":2
    }
    def check(msg):
        return msg.content in rps_dict and msg.author == ctx.author and msg.channel == ctx.channel
    rps_first_round = True
    winner = None
    gamble_data = read_json("gamble")
    if VERBOSE: await ctx.send(f"LOG rps start with user: {user}")
    while winner is None:
        if rps_first_round:
            await ctx.reply("「ぐー」「ちょき」「ぱー」で返信してね！\n最初はグ～、じゃんけん...")
        else:
            await ctx.reply("あいこでグ～、じゃんけん...")
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
            midgame_rps_users.remove(player_id)
            return
    if winner is not None:
        if winner == "player":
            await ctx.send("ま、負けた、、、")
            update_bal(gamble_data[user]+bet_amount*GAMBLE_RATES["rps"], user)
        else:
            await ctx.send("勝った！gg~")
        # update and display bal
        await ctx.invoke(bot.get_command("bal"))
        midgame_rps_users.remove(player_id)


# ADMIN COMMANDS    

@bot.command()
async def admin_get_num_inp(ctx):
    # register and check user is midbet
    player_id = ctx.message.author.id
    if player_id not in midbet_users:
        midbet_users.add(player_id)
    else:
        midbet_users.remove(player_id)
        return False
    await ctx.reply("how much to change？")
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
    try:
        res = await bot.wait_for("message", check=check, timeout=5)
        msg = res.content
        if check_is_num(msg):
            midbet_users.remove(player_id)
            return int(msg)
        else:
            midbet_users.remove(player_id)
            return False
    except asyncio.TimeoutError:
        midbet_users.remove(player_id)
        return False

@bot.command()
@commands.is_owner()
async def admin_change_money(ctx):
    gamble_data = read_json("gamble")
    user = ctx.author.name
    num = await ctx.invoke(bot.get_command("admin_get_num_inp"))
    if not num:
        return
    await ctx.reply(f"changing your bal from {gamble_data[user]} > {num}")
    update_bal(num, user)
    gamble_data = read_json("gamble")
    await ctx.reply(f"your new bal is {gamble_data[user]}")

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