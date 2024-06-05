import os
import discord
import json
import sys
import aiofiles
import datetime
import dateutil.parser
import typing
import re
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import PrettyHelp

# FUNC

def update_json(json_name:str, dict:dict):
    f = open(f"json/{json_name}.json",mode="w")
    json.dump(dict, f, indent=6, skipkeys=True)
    f.close()

def check_is_num(txt:str):
    try:
        val = int(txt)
        return True
    except:
        return False

def get_extensions():
    # COGS
    return [n.replace(".py","") for n in os.listdir("cogs") if n[-3:] == ".py"]

def get_guild_id():
    return 1243840681944813679

def clean_money_display(money:typing.Union[str,int]):
    try:
        formatted_money = f"{format(money,',')}:coin:"
        return formatted_money
    except Exception as e:
        print(f"Exception = {e}\ninput = {money}\ntype = {type(money)}")

def encode_datetime_timestamp(now:datetime.datetime):
    return {
        "year":now.year, 
        "month":now.month, 
        "day":now.day,
        "hour":now.hour,
        "minute":now.minute,
        "second":now.second
    }
def decode_datetime_timestamp(now:dict):
    return datetime.datetime(
        year=now["year"],
        month=now["month"],
        day=now["day"],
        hour=now["hour"],
        minute=now["minute"],
        second=now["second"],
        tzinfo=datetime.timezone.utc
    )

# ASYNCH

async def find_japanese_from_str(s):
    pattern = r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]'
    res = re.findall(pattern, s)
    return res

async def read_json(json_name:str):
    f = open(f"json/{json_name}.json")
    data = json.load(f)
    f.close()
    return data
    
async def check_user_in_gamble_data(gamble_data:dict, user:str):
    # if user_name not registed in json
    if user not in gamble_data:
        gamble_data[user] = 0
    return gamble_data
    
async def update_bal(amount:int, user:str):
    """
    amount [int]
    user_name = str [ctx.author.name]
    """
    gamble_data = await read_json("gamble")
    gamble_data = await check_user_in_gamble_data(gamble_data, user)
    gamble_data[user] = amount
    update_json("gamble", gamble_data)

async def update_bal_delta(amount:int, user:str):
    """
    amount [int]
    user_name += str [ctx.author.name]
    """
    gamble_data = await read_json("gamble")
    gamble_data = await check_user_in_gamble_data(gamble_data, user)
    gamble_data[user] += amount
    update_json("gamble", gamble_data)

# JSON ENCODER / DECODER

# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, (datetime.date, datetime.datetime)):
#             return obj.isoformat()
            
# def DecodeDateTime(empDict):
#    if 'joindate' in empDict:
#       empDict["joindate"] = dateutil.parser.parse(empDict["joindate"])
#       return empDict