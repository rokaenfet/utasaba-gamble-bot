from discord.ext import commands
from discord import app_commands
from funcs import *
import os
import time

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

    @commands.command(aliases = ["rock-paper-scissors, じゃんけん"])
    async def rps(self, ctx):
        # user in question
        user = ctx.author.name
        # ask how much they want to bet
        bet_amount = await ctx.invoke(self.bot.get_command("ask_for_num_input"))
        if not bet_amount:
            return
        # register and check user is mid-game
        player_id = ctx.message.author.id
        if self.VERBOSE: print(f"checking if {user} in {self.midgame_rps_users}")
        if player_id not in self.midgame_rps_users:
            self.midgame_rps_users.add(player_id)
            if self.VERBOSE: print(f"{user} registered in {self.midgame_rps_users}")
        else:
            await ctx.reply("もうじゃんけんしてるよ！早く手を出して！")
            if self.VERBOSE: print(f"{user} is already in a rps game")
            await update_bal_delta(bet_amount, user)
            return
        if self.VERBOSE: print(f"{user} passed mid-game check")
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
            return msg.content in rps_dict and msg.author == ctx.author and msg.channel == ctx.channel
        rps_first_round = True
        winner = None
        gamble_data = await read_json("gamble")
        # get embeds
        rps_init_embed = self.rps_init_embed()
        rps_alt_embed = self.rps_alt_embed()

        while winner is None:
            if rps_first_round:
                await ctx.reply(embed = rps_init_embed)
            else:
                await ctx.reply(embed = rps_alt_embed)
            try:
                res = await self.bot.wait_for("message", check=check, timeout=10.0)
                player_hand = res.content
                rps_first_round = False
                bot_hand = random.choice(["ぐー","ちょき","ぱー"])
                await ctx.send(f"{rps_num_hand_to_emoji_dict[rps_dict[bot_hand]]} {bot_hand}!")
                player_hand_num, bot_hand_num = rps_dict[player_hand], rps_dict[bot_hand]
                # check game end
                if (player_hand_num+1)%3 == bot_hand_num:
                    winner = "player"
                elif (bot_hand_num+1)%3 == player_hand_num:
                    winner = "bot"
            except asyncio.TimeoutError:
                self.midgame_rps_users.remove(player_id)
                await ctx.send("遅い！最初から！")
                await update_bal_delta(bet_amount, user)
                return
        if winner is not None:
            if winner == "player":
                await ctx.send("ま、負けた、、、")
                await update_bal(gamble_data[user]+bet_amount*self.GAMBLE_RATES["rps"], user)
            else:
                await ctx.send("勝った！gg~")
            # update and display bal
            self.midgame_rps_users.remove(player_id)
            await ctx.invoke(self.bot.get_command("bal"))
    
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