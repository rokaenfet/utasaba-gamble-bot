import os
import discord
import json
import asyncio
import sys
import random
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

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

def update_bal_delta(amount, user_name):
    """
    amount [int]
    user_name += str [ctx.author.name]
    """
    gamble_data = read_json("gamble")
    gamble_data[user_name] += amount
    update_json("gamble", gamble_data)

def get_extensions():
    # COGS
    return [n.replace(".py","") for n in os.listdir("cogs") if n[-3:] == ".py"]