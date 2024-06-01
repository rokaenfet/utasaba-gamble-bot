from discord.ext import commands
from discord import app_commands
from funcs import *
import typing
import os
import time
import asyncio
import random

class GambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.midbet_users = set()
        self.midgame_rps_users = set()
        self.GAMBLE_RATES = {
            "rps":3
        }
        self.VERBOSE = False

        self.image_urls = {
            "rps":"https://i0.wp.com/www.vampiretools.com/wp-content/uploads/2018/09/psr.jpg?fit=908%2C490&ssl=1"
        }

    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

    @app_commands.command(name="bal", description="show current balance of user")
    async def bal(self, interaction:discord.Interaction, user:discord.Member = None):
        """
        !bal
        get your bal / make new bank account if non-existing
        """
        gamble_data = await read_json("gamble")
        if user is None:
            user = interaction.user
        else:
            user = user 
        user_name = user.name
        if user_name not in gamble_data:
            gamble_data[user] =  0
        update_json("gamble", gamble_data)
        embed = discord.Embed(title=f":euro: 残高 :dollar:", description=f"{user.mention}の残高\n{gamble_data[user_name]:} :coin:", color=discord.Color.magenta())
        await interaction.response.send_message(embed=embed)

    @commands.command(hidden=True)
    async def ask_for_num_input(self, ctx):
        gamble_data = await read_json("gamble")
        # register and check user is midbet
        player_id = ctx.message.author.id
        if player_id not in self.midbet_users:
            self.midbet_users.add(player_id)
        else:
            self.midbet_users.remove(player_id)
            return False
        # user in question
        user = ctx.author.name
        # ask how much to bet
        await ctx.reply(f"{user}の残高:{gamble_data[user]}ロカ。いくら賭ける？")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            # wait for res
            res = await self.bot.wait_for("message", check=check, timeout=5)
            msg = res.content
            # check for all-ins
            if msg.lower() in ("all","オール","オールイン","おーる","おーるいん"):
                if gamble_data[user] <= 0:
                    ctx.reply(f"まずは金を用意しな")
                    return
                await ctx.reply(f"{gamble_data[user]},全財産オールインだ！")
                self.midbet_users.remove(player_id)
                await update_bal(0, user)
                return gamble_data[user]
            # check inp is an int
            if check_is_num(msg):
                self.midbet_users.remove(player_id)
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
                    await update_bal(gamble_data[user]-num, user)
                    return num
            # catch non-int (float inc)
            else:
                await ctx.reply("数字を入れてください...")
                self.midbet_users.remove(player_id)
                return False
        # response timeout
        except asyncio.TimeoutError:
            await ctx.reply("判断が（返信が）遅い！")
            self.midbet_users.remove(player_id)
            return False

    @app_commands.command(name="rps", description="ギャンブルジャンケン")
    @app_commands.describe(
        bet_amount="賭け金・'all'でオールイン、または数字入力でその額をベット",
        opponent="相手となる@[ユーザー名]。入力なしでボット相手に変更"
    )
    async def rps(self, interaction:discord.Interaction, bet_amount:str, opponent:discord.Member = None):
        # user in question
        user = interaction.user
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
                await interaction.response.send_message(embed=discord.Embed(
                    title=":money_with_wings:ALL-IN:exclamation:",
                    description=f"{user.mention}はじゃんけんに**全額ベット**しました:bangbang: 賭け金={bet_amount}:coin:",
                    color=discord.Color.light_embed()
                ))
                await update_bal(0, user_name)
            # if not all in
            else:
                try:
                    # if bet_amount : int
                    bet_amount = int(bet_amount)
                    # if user have enough balance
                    if bet_amount < gamble_data[user_name]:
                        await interaction.response.send_message(embed=discord.Embed(
                            title=":money_with_wings:じゃんけん | ギャンブル:money_with_wings:",
                            description=f"{user.mention}はじゃんけんに{bet_amount}:coin:賭けました",
                            color=discord.Color.yellow()
                        ))
                        await update_bal_delta(-bet_amount, user_name)
                    # if its effectively an all in
                    elif bet_amount == gamble_data[user_name]:
                        await interaction.response.send_message(embed=discord.Embed(
                            title=f":money_with_wings:じゃんけん | ALL-IN:exclamation:",
                            description="{user.mention}はじゃんけんに**全額ベット**しました:bangbang: 賭け金は{bet_amount}:coin:",
                            color=discord.Color.light_embed()
                        ))
                        await update_bal(0, user_name)
                    # if user doesn't have enough balance
                    else:
                        await interaction.response.send_message(embed=discord.Embed(
                            title=":x:じゃんけんゲーム無効:bangbang:", 
                            description=f"{user.mention}様の残高は{gamble_data[user_name]}:coin:です。それ以下で賭けてください。", 
                            color=discord.Color.red()
                        ))
                # not an integer and not all in
                except:
                    await interaction.response.send_message("{user.mention}様、数字か「`all`」か「`オール`」を入力してください")
                    return
        
                
        # opponent in question
        if opponent is None:
            opponent = self.bot.user
            opponent_is_bot = True
        else:
            opponent_is_bot = False
        opponent_name = opponent.name
        print(f"user:{user}, {user_name}\nopponent:{opponent},{opponent_name}")

        # TEMP!!! OPPONENT ALWAYS BOT
        opponent_is_bot = True
        opponent_name = self.bot.user
        opponent_name = opponent.name

        # load rps
        rps_dict = {
            "ぐー":0,
            "ちょき":1,
            "ぱー":2
        }
        rps_num_hand_to_emoji_dict = {
            0:":fist:",
            1:":v:",
            2:":raised_hand:"
        }
        def check(msg):
            return msg.content in rps_dict and msg.author == user and msg.channel == interaction.channel
        
        rps_first_round = True
        winner = None
        gamble_data = await read_json("gamble")
        # get embeds
        rps_init_embed = self.rps_init_embed()
        rps_alt_embed = self.rps_alt_embed()

        while winner is None:
            if rps_first_round:
                await interaction.followup.send(embed = rps_init_embed)
            else:
                await interaction.followup.send(embed = rps_alt_embed)
            try:
                res = await self.bot.wait_for("message", check=check, timeout=10.0)
                player_hand = res.content
                rps_first_round = False
                bot_hand = random.choice(["ぐー","ちょき","ぱー"])
                await interaction.followup.send(embed = discord.Embed(title=f"ポン！僕の手は {bot_hand}:grey_exclamation:"))
                player_hand_num, bot_hand_num = rps_dict[player_hand], rps_dict[bot_hand]
                # check game end
                if (player_hand_num+1)%3 == bot_hand_num:
                    winner = "player"
                elif (bot_hand_num+1)%3 == player_hand_num:
                    winner = "bot"
            except asyncio.TimeoutError:
                # self.midgame_rps_users.remove(player_id)
                await interaction.followup.send("もっと早く手をだして！最初から :person_shrugging:")
                await update_bal_delta(bet_amount, user_name)
                return
        if winner is not None:
            if winner == "player":
                win_amount = bet_amount*self.GAMBLE_RATES["rps"]
                await update_bal_delta(win_amount, user_name)
                gamble_data = await read_json("gamble")
                await interaction.followup.send(embed = discord.Embed(
                    title = "YOU WIN!! :crown:", 
                    description=f"{user.mention}は{win_amount}:coin:勝ちました！\n現在の残高は{gamble_data[user_name]}:coin:です"))
            else:
                lose_amount = bet_amount
                await interaction.followup.send(embed = discord.Embed(
                    title = "YOU LOSE :regional_indicator_l: :sob:", 
                    description=f"{user.mention}は{lose_amount}:coin:負けたよ、、、\n現在の残高は{gamble_data[user_name]}:coin:です"))
    
    @app_commands.command(name="reload_player_sets", description="remove players from in-game list")
    @commands.is_owner()
    async def reload_player_sets(self, interaction:discord.Interaction):
        self.midbet_users = set()
        self.midgame_rps_users = set()
        embed = discord.Embed(title="set_reset", description=f"In-Game sets reset complete :D", color=discord.Color.brand_green())
        await interaction.response.send_message(embed=embed)

    def rps_init_embed(self):
        embed=discord.Embed(title="じゃんけん! :fist: :raised_hand: :v:", color=discord.Color.blurple())
        embed.add_field(name=":fist:　ぐー", value="", inline=False)
        embed.add_field(name=":raised_hand:　ぱー", value="", inline=False)
        embed.add_field(name=":v:　ちょき", value="", inline=False)
        embed.set_footer(text="チャットに「ぐー」「ちょき」「ぱー」と書いてね")
        embed.set_image(url=self.image_urls["rps"])
        return embed
    
    def rps_alt_embed(self):
        embed=discord.Embed(title="あいこでグ～　じゃんけん、、、", color=discord.Color.blurple())
        embed.add_field(name=":fist:　ぐー", value="", inline=False)
        embed.add_field(name=":raised_hand:　ぱー", value="", inline=False)
        embed.add_field(name=":v:　ちょき", value="", inline=False)
        return embed

async def setup(bot):
    await bot.add_cog(GambleCog(bot), guilds=[discord.Object(id=get_guild_id())])