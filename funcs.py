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
import langdetect
from discord.ext import commands
from dotenv import load_dotenv
from dotenv import load_dotenv


langdetect.DetectorFactory.seed = 0

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

def find_string_between_bracket(s:str):
    return s[s.find("(")+1:s.find(")")]

def translate_jp_bracket_to_eng_bracket(s:str):
    bracket_trans_dict = {
        "（":"(",
        "）":")"
    }
    return "".join([n if n not in bracket_trans_dict else bracket_trans_dict[n] for n in s])

def load_bot_token():
    load_dotenv("token.env")
    return os.environ.get("DISCORD_TOKEN")

def load_giphy_token():
    load_dotenv("token.env")
    return os.environ.get("GIPHY_KEY")

def rps_init_embed():
    embed=discord.Embed(title="じゃんけん! :fist: :raised_hand: :v:", color=discord.Color.blurple())
    embed.add_field(name=":fist:　ぐー", value="", inline=False)
    embed.add_field(name=":raised_hand:　ぱー", value="", inline=False)
    embed.add_field(name=":v:　ちょき", value="", inline=False)
    embed.set_footer(text="チャットに「ぐー」「ちょき」「ぱー」と書いてね")
    embed.set_image(url="https://i0.wp.com/www.vampiretools.com/wp-content/uploads/2018/09/psr.jpg?fit=908%2C490&ssl=1")
    return embed

def rps_alt_embed():
    embed=discord.Embed(title="あいこでグ～　じゃんけん、、、", color=discord.Color.blurple())
    embed.add_field(name=":fist:　ぐー", value="", inline=False)
    embed.add_field(name=":raised_hand:　ぱー", value="", inline=False)
    embed.add_field(name=":v:　ちょき", value="", inline=False)
    return embed

def char_is_hiragana(c) -> bool:
    return u'\u3040' <= c <= u'\u309F' or c == "ー"

def string_is_hiragana(s: str) -> bool:
    return all(char_is_hiragana(c) for c in s)

def check_str_validity_for_shiritori(msg: str):
    """
    get str content
    convert jp / en brackets to en brackets
    extract string between brackets
    strip special chars such as ! or ?
    turn all katakana to hiragana
    detect string between bracket is japanese
    detect string between bracket is hiragana
    """
    try:
        msg = translate_jp_bracket_to_eng_bracket(msg)
        msg = find_string_between_bracket(msg)
        msg = strip_special_chars(msg)
        msg = jaconv.kata2hira(msg)
        # print(f"{msg} is {langdetect.detect_langs(msg)}")
        if langdetect.detect(msg) == "ja":
            if string_is_hiragana(msg):
                if msg[-1] != "ん":
                    return msg
    except Exception as e:
        print(f"Error in check_str_validity_for_shiritori(msg:str) -> bool\n{e}")


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
    gamble_data[user] = int(amount)
    update_json("gamble", gamble_data)

async def update_bal_delta(amount:int, user:str):
    """
    amount [int]
    user_name += str [ctx.author.name]
    """
    gamble_data = await read_json("gamble")
    gamble_data = await check_user_in_gamble_data(gamble_data, user)
    gamble_data[user] += int(amount)
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
    messages = [message async for message in text_channel.history(limit=500) if message.author.name != bot.user.name]
    # filter only messages with ()
    messages_w_bracket = [n for n in messages if "(" in n.content and ")" in n.content]
    if len(messages_w_bracket) == 0:
        await text_channel.send(f"(しりとり)")
        update_json("shiritori", {"last_message":"しりとり", "user":bot.user.name, "history":["(しりとり)"]})
    else:
        # check / change messages
        new_msgs = []
        for msg in messages_w_bracket:
            msg = msg.content
            new_msg = check_str_validity_for_shiritori(msg)
            if new_msg:
                new_msgs.append(new_msg)
        update_json("shiritori", {"last_message":"", "user":"", "history": new_msgs})
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
                
    # current message
    cur_msg_content = msg.content
    cur_msg_content = check_str_validity_for_shiritori(cur_msg_content)
    if cur_msg_content is None:
        await msg.add_reaction(str("❌"))
        await msg.channel.send(f"しりとりの言葉は**ひらがな**か**カタカナ**_だけ_を`()`に入れてね:exclamation:\n例入力: `歌う(うたう)`")
        return

    shiritori_data = await read_json("shiritori")
    # last message
    last_word = shiritori_data["history"][-1]
    # check 伸ばし棒
    last_char = last_word[-2] if last_word[-1] == "ー" else last_word[-1]
    # katakana > hiragana
    last_char = jaconv.kata2hira(last_char)
    # check small case ending
    last_char = trans_dict[last_char] if last_char in trans_dict else last_char

    # check non duplicate
    if cur_msg_content in shiritori_data["history"]:
        await msg.add_reaction(str("❌"))
        await msg.channel.send(f"その言葉はもう使われたよ:exclamation:")
        return
    # check ending valid
    if cur_msg_content[-1] == "ん":
        await msg.add_reaction(str("❌"))
        await msg.channel.send(f"`ん`だと終わってしまう、、、:exclamation:")
        return
    if  cur_msg_content[0] == last_char:
        update_json("shiritori",{
            "last_message":cur_msg_content,
            "user":msg.author.name, 
            "history":shiritori_data["history"]+[cur_msg_content]
            })
        await update_bal_delta(100, msg.author.name)
        await msg.add_reaction(str("✅"))
    else:
        await msg.add_reaction(str("❌"))
        await msg.channel.send(f"現在の言葉は`{shiritori_data['history'][-1]}`です:exclamation:")

async def on_message_image_upload_daily(msg:discord.Message):
    # json file name
    json_f = "image_daily"
    # channel
    channel = msg.channel
    channel_id = str(channel.id)
    # user
    user_name = msg.author.name
    # check msg has img attachment
    attachments = msg.attachments
    if len(attachments) > 0:
        # get relevent image daily reward channel's data
        data = await read_json(json_f)

        # daily prep
        cur_time = datetime.datetime.now(datetime.timezone.utc)
        fortnite_time = cur_time - datetime.timedelta(days=2)

        # check for new users in image_daily.json[channel.id]
        if user_name not in data[channel_id]["users"]:
            data[channel_id]["users"][user_name] = {
                "streak":0,
                "last_daily": encode_datetime_timestamp(fortnite_time)
            }
        update_json(json_f, data)

        user_data = data[channel_id]["users"][user_name]

        # if its been more than a day, allow daily
        user_last_daily_time = decode_datetime_timestamp(user_data["last_daily"])
        delta_time = cur_time - user_last_daily_time
        can_get_daily = delta_time.days >= 1

        # reset streak if 2 days has passed
        if delta_time.days >= 2:
            streak = 0
        else:
            streak = user_data["streak"]
        
        # responses
        if can_get_daily:
            # add streak
            streak += 1
            # add money
            await update_bal_delta(amount = 1000, user = user_name)
            await msg.add_reaction(str("✅"))
            # update json w new streak and timestamp
            data[channel_id]["users"][user_name] = {
                "streak":streak, 
                "last_daily": encode_datetime_timestamp(cur_time)
                }
            update_json(json_f, data)
        else:
            # add less money
            await update_bal_delta(amount = 100, user = user_name)
            await msg.add_reaction(str("🔥"))

async def display_win_loss_result(win:bool, bet_amount:int, user:discord.Member, gamble_name:str, rates:float):
        user_name = user.name
        gamble_data = await read_json("gamble")
        if win:
            win_amount = int(bet_amount*rates)
            await update_bal_delta(win_amount, user_name)
            gamble_data = await read_json("gamble")
            embed = discord.Embed(
                title = f"{gamble_name}ギャンブル **YOU WIN**:bangbang: :crown:", 
                description=f"{user.mention}は{clean_money_display(win_amount)}勝ちました！\n現在の残高は{clean_money_display(gamble_data[user_name])}です",
                color=discord.Color.purple()
            )
        else:
            lose_amount = bet_amount
            embed = discord.Embed(
                title = f":regional_indicator_l: {gamble_name}ギャンブル **YOU LOSE**... :sob:", 
                description=f"{user.mention}は{clean_money_display(lose_amount)}負けたよ、、、\n現在の残高は{clean_money_display(gamble_data[user_name])}です",
                color=discord.Color.blue()
            )
        return embed

async def check_bet_amount(bet_amount:str, user:discord.Member, game_name:str):
    response = None
    user_name = user.name

    # check user's bal's existence
    gamble_data = await read_json("gamble")
    # get data
    gamble_data = await check_user_in_gamble_data(gamble_data, user_name)

    # if bet_amount : str
    if isinstance(bet_amount, str):
        # is bet_amount == all in
        if bet_amount.lower() in {"all","オール"}:
            bet_amount = gamble_data[user_name]
            response = discord.Embed(
                title=f":money_with_wings:ALL-IN:exclamation:",
                description=f"{user.mention}は{game_name}に**全額ベット**しました:bangbang: 賭け金 = **{clean_money_display(bet_amount)}**",
                color=discord.Color.light_embed()
            )
            await update_bal(0, user_name)
        # if not all in
        else:
            try:
                # bet_amount : str > int (check can it be turned to int)
                bet_amount = int(bet_amount)
                # if user have enough balance
                if bet_amount < gamble_data[user_name]:
                    response = discord.Embed(
                        title=f":money_with_wings:{game_name} | ギャンブル:money_with_wings:",
                        description=f"{user.mention}は{game_name}に{clean_money_display(bet_amount)}賭けました",
                        color=discord.Color.yellow()
                    )
                    await update_bal_delta(-bet_amount, user_name)
                # if its effectively an all in
                elif bet_amount == gamble_data[user_name]:
                    response = discord.Embed(
                        title=f":money_with_wings:{game_name} | ALL-IN:exclamation:",
                        description=f"{user.mention}は**{game_name}**に**全額ベット**しました:bangbang: 賭け金は{clean_money_display(bet_amount)}",
                        color=discord.Color.light_embed()
                    )
                    await update_bal(0, user_name)
                # if user doesn't have enough balance
                else:
                    response = discord.Embed(
                        title=f":x:{game_name}ゲーム無効:bangbang:", 
                        description=f"{user.mention}様の残高は{clean_money_display(gamble_data[user_name])}です。それ以下で賭けてください。", 
                        color=discord.Color.red()
                    )
                    bet_amount = None
            # not an integer and not all in
            except:
                response = f"{user.mention}様、数字か「`all`」か「`オール`」を入力してください"
                bet_amount = None
    # return response to /command invoking this function
    return response, bet_amount