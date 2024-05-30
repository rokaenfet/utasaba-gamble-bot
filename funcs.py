import os
import discord
import json
import sys
import aiofiles
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

async def read_json(json_name):
    f = open(f"json/{json_name}.json")
    data = json.load(f)
    f.close()
    return data

def update_json(json_name, dict):
    f = open(f"json/{json_name}.json",mode="w")
    json.dump(dict, f, indent=6, skipkeys=True)
    f.close()

def check_is_num(txt):
    try:
        val = int(txt)
        return True
    except:
        return False
    
async def check_user_in_gamble_data(gamble_data, user):
    # if user_name not registed in json
    if user not in gamble_data:
        gamble_data[user] = 0
    return gamble_data
    
async def update_bal(amount, user):
    """
    amount [int]
    user_name = str [ctx.author.name]
    """
    gamble_data = await read_json("gamble")
    gamble_data = await check_user_in_gamble_data(gamble_data, user)
    gamble_data[user] = amount
    update_json("gamble", gamble_data)

async def update_bal_delta(amount, user):
    """
    amount [int]
    user_name += str [ctx.author.name]
    """
    gamble_data = await read_json("gamble")
    gamble_data = check_user_in_gamble_data(gamble_data, user)
    gamble_data[user] += amount
    update_json("gamble", gamble_data)

def get_extensions():
    # COGS
    return [n.replace(".py","") for n in os.listdir("cogs") if n[-3:] == ".py"]

def get_guild_id():
    return 1243840681944813679