import os
import discord
import json
import sys
import aiofiles
import datetime
import dateutil.parser
import typing
import re
import time
import jaconv
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

def strip_special_chars(msg_str:str):
    special_chars = ["!","！",",",".","。","?","？"]
    for specials in special_chars:
        msg_str = msg_str.replace(specials,"")
    return msg_str

def small_to_large_jp_trans(strj): #小文字を大文字に変換する関数
    moji = str.maketrans("ァィゥェォャッュョ", "アイウエオヤユツヨ")
    return strj.translate(moji)

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

# SHIRITORI
async def shiritori_on_ready(bot:commands.Bot, TEXT_CHANNEL_ID:int):
    """
    bot:discord.ext.commands.Bot
    TEXT_CHANNEL_ID:int
    get [TEXT_CHANNEL_ID]'s history, saves 100 past messages and last message and sent user into shiritori.json
    """
    # load specified text_channel's history
    text_channel = bot.get_channel(TEXT_CHANNEL_ID)
    # order from oldest = [0], newest = [-1]
    t = time.time()
    messages = [message async for message in text_channel.history(limit=100)]
    if len(messages) == 0:
        await text_channel.send(f"しりとり")
        update_json("shiritori", {"last_message":"しりとり", "user":bot.user.name, "history":["しりとり"]})
    else:
        # check for last message which doesn't end in ん and is all japanese
        for msg in messages:
            msg_str = msg.content
            # strip special chars
            msg_str = strip_special_chars(msg_str)
            jp_chars = await find_japanese_from_str(msg_str)
            if len(jp_chars) > 0 and len(jp_chars) == len(msg_str) and msg_str[-1] != "ん":
                break
        update_json("shiritori", {"last_message":msg_str, "user":msg.author.name, "history": [n.content for n in messages]})
    print(f"loaded all msg in #{text_channel}. Load time: {round(time.time()-t,3)}s")


# ON_MESSAGE_SEND

async def shiritori_on_message(msg:discord.Message):
    """
    msg:discord.Message
    if msg is in the shiritori text channel and is not from this bot
    check if msg is a valid shiritori word
    """
    trans_dict = {
        "ぁ":"あ",
        "ぃ":"い",
        "ぅ":"う",
        "ぇ":"え",
        "ぉ":"お",
        "ゃ":"や",
        "ゅ":"ゆ",
        "っ":"つ"
    }
    shiritori_data = await read_json("shiritori")
    # last message
    last_word = shiritori_data["last_message"]
    # check 伸ばし棒
    last_char = last_word[-2] if last_word[-1] == "ー" else last_word[-1]
    # katakana > hiragana
    last_char = jaconv.kata2hira(last_char)
    # check small case ending
    last_char = trans_dict[last_char] if last_char in trans_dict else last_char

    # current message
    cur_msg_content = msg.content
    # strip special characters from msg
    stripped_cur_msg_content = strip_special_chars(cur_msg_content)
    if stripped_cur_msg_content[-1] != "ん" and stripped_cur_msg_content[0] == last_char and stripped_cur_msg_content not in shiritori_data["history"]:
        update_json("shiritori",{
            "last_message":stripped_cur_msg_content,
            "user":msg.author.name, 
            "history":shiritori_data["history"]+[stripped_cur_msg_content]
            })
        await update_bal_delta(100, msg.author.name)
        await msg.add_reaction(str("✅"))
    else:
        await msg.add_reaction(str("❌"))
        await msg.channel.send(f"現在の言葉は`{shiritori_data['last_message']}`です:exclamation:")


# JSON ENCODER / DECODER

# class DateTimeEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, (datetime.date, datetime.datetime)):
#             return obj.isoformat()
            
# def DecodeDateTime(empDict):
#    if 'joindate' in empDict:
#       empDict["joindate"] = dateutil.parser.parse(empDict["joindate"])
#       return empDict