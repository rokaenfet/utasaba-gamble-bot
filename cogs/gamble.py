from discord.ext import commands
from funcs import *

class GambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.midbet_users = set()
        self.midrps_users = set()
        self.GAMBLE_RATES = {
            "rps":3
        }

    @commands.command()
    async def bal(self, ctx):
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

    @commands.command(hidden=True)
    async def ask_for_num_input(self, ctx):
        gamble_data = read_json("gamble")
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
        await ctx.reply("いくら賭ける？")
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
                update_bal(0, user)
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
                    update_bal(gamble_data[user]-num, user)
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
        if player_id not in self.midgame_rps_users:
            self.midgame_rps_users.add(player_id)
        else:
            await ctx.reply("もうじゃんけんしてるよ！早く手を出して！")
            return
        # load rps
        rps_dict = {
            "ぐー":0,
            "ちょき":1,
            "ぱー":2
        }
        def check(msg):
            return msg.content in rps_dict and msg.author == ctx.author and msg.channel == ctx.channel
        rps_first_round = True
        winner = None
        await ctx.send("TEST")
        gamble_data = read_json("gamble")
        while winner is None:
            if rps_first_round:
                await ctx.reply("「ぐー」「ちょき」「ぱー」で返信してね！\n最初はグ～、じゃんけん...")
            else:
                await ctx.reply("あいこでグ～、じゃんけん...")
            try:
                res = await self.bot.wait_for("message", check=check, timeout=10.0)
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
                self.midgame_rps_users.remove(player_id)
                return
        if winner is not None:
            if winner == "player":
                await ctx.send("ま、負けた、、、")
                update_bal(gamble_data[user]+bet_amount*self.GAMBLE_RATES["rps"], user)
            else:
                await ctx.send("勝った！gg~")
            # update and display bal
            await ctx.invoke(self.bot.get_command("bal"))
            self.midgame_rps_users.remove(player_id)

async def setup(bot):
    await bot.add_cog(GambleCog(bot))