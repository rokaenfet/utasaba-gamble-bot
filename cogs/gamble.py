from discord.ext import commands
from discord import app_commands
from funcs import *
import typing
import os
import time
import asyncio
import random
from random import shuffle
from commands_argument import get_all_commands

ALL_COMMANDS = get_all_commands()

class GambleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.midbet_users = set()
        self.midgame_rps_users = set()
        self.GAMBLE_RATES = {
            "rps":2.5,
            "flip":2,
            "blackjack":2
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

    @app_commands.command(name=ALL_COMMANDS.gamble.bal.name, description=ALL_COMMANDS.gamble.bal.description)
    @app_commands.describe(
        user=ALL_COMMANDS.gamble.bal.user
    )
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
        gamble_data = await check_user_in_gamble_data(gamble_data, user_name)
        update_json("gamble", gamble_data)
        embed = discord.Embed(title=f":euro: 残高 :dollar:", description=f"{user.mention}の残高\n{clean_money_display(gamble_data[user_name])}", color=discord.Color.magenta())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=ALL_COMMANDS.gamble.flip.name, description=ALL_COMMANDS.gamble.flip.description)
    @app_commands.describe(
        bet_amount=ALL_COMMANDS.gamble.flip.bet_amount,
        side=ALL_COMMANDS.gamble.flip.side
    )
    async def flip(self, interaction:discord.Interaction, bet_amount:str, side:str = "表"):
        # user in qs
        user = interaction.user
        user_name = user.name

        if side not in ("表","おもて","オモテ","裏","うら","ウラ"):
            await interaction.response.send_message(f"「表」か「裏」と入力してください:exclamation:")
            return

        # check bet_amount, and get reply message [str | embed] and bet_amout [int]
        bet_amount_check_response, bet_amount = await self.check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="gamble"
            )
        if isinstance(bet_amount_check_response, str):
            await interaction.response.send_message(bet_amount_check_response)
        elif isinstance(bet_amount_check_response, discord.Embed):
            await interaction.response.send_message(embed=bet_amount_check_response)
        else:
            print(f"invalid return of {type(bet_amount_check_response)}")
            return
        
        # get win/loss
        win = random.choice((0,1)) == 0
        # get response
        response = await self.display_win_loss_result(
            win = win, 
            bet_amount = bet_amount, 
            user = user, 
            gamble_name = "コイン",
            rates = self.GAMBLE_RATES["flip"]
            )
        await interaction.followup.send(embed=response)


    @app_commands.command(name=ALL_COMMANDS.gamble.rps.name, description=ALL_COMMANDS.gamble.rps.description)
    @app_commands.describe(
        bet_amount=ALL_COMMANDS.gamble.rps.bet_amount
    )
    async def rps(self, interaction:discord.Interaction, bet_amount:str):
        """
        TO-DO
        handle when no input for bet_amount
        """
        
        # user in question
        user = interaction.user
        user_name = user.name

        # check bet_amount, and get reply message [str | embed] and bet_amout [int]
        bet_amount_check_response, bet_amount = await self.check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="gamble"
            )
        if isinstance(bet_amount_check_response, str):
            await interaction.response.send_message(bet_amount_check_response)
        elif isinstance(bet_amount_check_response, discord.Embed):
            await interaction.response.send_message(embed=bet_amount_check_response)
        else:
            print(f"invalid return of {type(bet_amount_check_response)}")
            return

        # load rps
        rps_dict = {
            "ぐー":0,
            "ちょき":1,
            "ぱー":2
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
                await interaction.followup.send(embed = discord.Embed(title=f"ポン:grey_exclamation:僕の手は {bot_hand}:grey_exclamation:"))
                player_hand_num, bot_hand_num = rps_dict[player_hand], rps_dict[bot_hand]
                # check game end
                if (player_hand_num+1)%3 == bot_hand_num:
                    winner = "player"
                elif (bot_hand_num+1)%3 == player_hand_num:
                    winner = "bot"
            except asyncio.TimeoutError:
                await interaction.followup.send("もっと早く手をだして:exclamation:最初から :person_shrugging:")
                await update_bal_delta(bet_amount, user_name)
                return
        if winner is not None:
            win = winner == "player"
            response = await self.display_win_loss_result(
                win = win, 
                bet_amount = bet_amount, 
                user = user, 
                gamble_name="じゃんけん",
                rates = self.GAMBLE_RATES["rps"]
                )
            await interaction.followup.send(embed = response)

<<<<<<< HEAD
=======
    
    # async def blackjack(self, interaction:discord.Interaction, bet_amount:str, opponent:discord.Member = None): 
    #     bet_amount_check_response, bet_amount = await self.check_bet_amount(
    #         bet_amount=bet_amount, 
    #         user=user, 
    #         game_name="gamble"
    #         )
        
    #     cards = {"A" : 1, "2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "10" : 10, "J" : 10, "Q" : 10, "K" : 10}
    #     deck = []

    #     def genDeck():
    #         deck = []
    #         # Generate a deck of 6 packs
    #         for _ in range(6):
    #             pack = []
    #             # Generate each pack
    #             for i in range(4):
    #                 pack += cards.keys()
    #                 shuffle(pack)
    #             deck += pack
    #             shuffle(deck)
    #         return deck
        
    #     def deal(): 
    #         player_hand.append(deck.pop())
    #         dealer_hand.append(deck.pop())

            
    #     def sumHand(hand): 
    #         hand_sum = 0
    #         aces = 0
    #         for i in hand:
    #             if i != 'A': 
    #                 hand_sum += cards[i]
    #             else: 
    #                 aces += 1
    #         for i in range(aces): 
    #             if hand_sum + 11 <= 21: 
    #                 hand_sum += 11
    #             else: 
    #                 hand_sum += 1
    #         return hand_sum
        
    #     winner = None
    #     player_hand = []
    #     dealer_hand = []
    #     player_value = 0
    #     dealer_value = 0
    #     for _ in range(2): 
    #         player_hand.append(deck.pop())
    #         dealer_hand.append(deck.pop())
    #     player_value = sumHand(player_hand)
    #     dealer_value = sumHand(player_hand)
    #     if player_hand == 21 and dealer_hand != 21: 
    #         winner = True
    #     while winner is None: 
    #         #TODO add rest of game, hitting and staying
    #         try:
    #             await interaction.followup.send(embed = discord.Embed(title= player_hand))
    #             res = await self.bot.wait_for("message", check=check, timeout=10.0)
    #             # check game end
                
    #         except asyncio.TimeoutError:
    #             await interaction.followup.send("もっと早く手をだして:exclamation:最初から :person_shrugging:")
    #             await update_bal_delta(bet_amount, user_name)
    #             return
    #     if winner is not None:
    #         win = winner == "player"
    #         response = await self.display_win_loss_result(
    #             win = win, 
    #             bet_amount = bet_amount, 
    #             user = user, 
    #             gamble_name="BlackJack",
    #             rates = self.GAMBLE_RATES["rps"]
    #             )
    #         await interaction.followup.send(embed = response)
            
    @app_commands.command(name=ALL_COMMANDS.gamble.reload_player_sets.name, description=ALL_COMMANDS.gamble.reload_player_sets.description)
    @commands.is_owner()
    async def reload_player_sets(self, interaction:discord.Interaction):
        self.midbet_users = set()
        self.midgame_rps_users = set()
        embed = discord.Embed(title="set_reset", description=f"In-Game sets reset complete :D", color=discord.Color.brand_green())
        await interaction.response.send_message(embed=embed)

    async def display_win_loss_result(self, win:bool, bet_amount:int, user, gamble_name:str, rates:float):
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

    async def check_bet_amount(self, bet_amount, user, game_name):
        response = None
        user_name = user.name
        bet_amount_response = None

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
                    description=f"{user.mention}は{game_name}に**全額ベット**しました:bangbang: 賭け金={clean_money_display(bet_amount)}",
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
                            description=f"{user.mention}は{game_name}に**全額ベット**しました:bangbang: 賭け金は{clean_money_display(bet_amount)}",
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
                # not an integer and not all in
                except:
                    response = f"{user.mention}様、数字か「`all`」か「`オール`」を入力してください"
        # return response to /command invoking this function
        return response, bet_amount

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