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
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.midbet_users = set()
        self.midgame_rps_users = set()
        self.GAMBLE_RATES = {
            "rps":2.5,
            "flip":2,
            "blackjack":2,
            "russian_roulette":1.8
        }
        self.VERBOSE = False

        # rl_multi
        self.rl_multi_participants = []

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
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        bet_amount_check_response, bet_amount = await check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="コイントス"
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
        response = await display_win_loss_result(
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
        bet_amount_check_response, bet_amount = await check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="ジャンケン"
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

        def check(msg:discord.Message):
            return msg.content in rps_dict and msg.author == user and msg.channel == interaction.channel
        
        rps_first_round = True
        winner = None
        gamble_data = await read_json("gamble")

        while winner is None:
            if rps_first_round:
                await interaction.followup.send(embed = rps_init_embed())
            else:
                await interaction.followup.send(embed = rps_alt_embed())
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
            response = await display_win_loss_result(
                win = win, 
                bet_amount = bet_amount, 
                user = user, 
                gamble_name="じゃんけん",
                rates = self.GAMBLE_RATES["rps"]
                )
            await interaction.followup.send(embed = response)
    
    async def blackjack(self, interaction:discord.Interaction, bet_amount:str, opponent:discord.Member = None): 

        user = interaction.user
        user_name = user.name
        
        bet_amount_check_response, bet_amount = await check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="gamble"
            )
        
        cards = {"A" : 1, "2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "10" : 10, "J" : 10, "Q" : 10, "K" : 10}
        deck = []

        def genDeck():
            deck = []
            # Generate a deck of 6 packs
            for _ in range(6):
                pack = []
                # Generate each pack
                for i in range(4):
                    pack += cards.keys()
                    shuffle(pack)
                deck += pack
                shuffle(deck)
            return deck
        
        def deal(): 
            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())

            
        def sumHand(hand): 
            hand_sum = 0
            aces = 0
            for i in hand:
                if i != 'A': 
                    hand_sum += cards[i]
                else: 
                    aces += 1
            for i in range(aces): 
                if hand_sum + 11 <= 21: 
                    hand_sum += 11
                else: 
                    hand_sum += 1
            return hand_sum
        
        winner = None
        player_hand = []
        dealer_hand = []
        player_value = 0
        dealer_value = 0
        for _ in range(2): 
            player_hand.append(deck.pop())
            dealer_hand.append(deck.pop())
        player_value = sumHand(player_hand)
        dealer_value = sumHand(player_hand)
        if player_hand == 21 and dealer_hand != 21: 
            winner = True
        while winner is None: 
            #TODO add rest of game, hitting and staying
            try:
                await interaction.followup.send(embed = discord.Embed(title= player_hand))
                # res = await self.bot.wait_for("message", check=check, timeout=10.0)
                # check game end
                
            except asyncio.TimeoutError:
                await interaction.followup.send("need to hit or stay")
                await update_bal_delta(bet_amount, user_name)
                return
        if winner is not None:
            win = winner == "player"
            response = await display_win_loss_result(
                win = win, 
                bet_amount = bet_amount, 
                user = user, 
                gamble_name="BlackJack",
                rates = self.GAMBLE_RATES["rps"]
                )
            await interaction.followup.send(embed = response)
            
    @app_commands.command(name=ALL_COMMANDS.gamble.reload_player_sets.name, description=ALL_COMMANDS.gamble.reload_player_sets.description)
    @commands.has_role("Admin")
    async def reload_player_sets(self, interaction:discord.Interaction):
        self.midbet_users = set()
        self.midgame_rps_users = set()
        embed = discord.Embed(title="set_reset", description=f"In-Game sets reset complete :D", color=discord.Color.brand_green())
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name=ALL_COMMANDS.gamble.rl.name, description=ALL_COMMANDS.gamble.rl.description)
    @app_commands.describe(
        bet_amount=ALL_COMMANDS.gamble.rl.bet_amount
    )
    async def rl(self, interaction:discord.Interaction, bet_amount:str):
        # defer for slow response
        await interaction.response.defer()
        # user in question
        user = interaction.user
        user_name = user.name

        # check bet_amount, and get reply message [str | embed] and bet_amout [int]
        bet_amount_check_response, bet_amount = await check_bet_amount(
            bet_amount=bet_amount, 
            user=user, 
            game_name="一人ロシアンルーレット"
            )
        if isinstance(bet_amount_check_response, str):
            await interaction.followup.send(bet_amount_check_response)
        elif isinstance(bet_amount_check_response, discord.Embed):
            await interaction.followup.send(embed=bet_amount_check_response)
        else:
            print(f"invalid return of {type(bet_amount_check_response)}")
            return
        
        # rl embed
        embed = discord.Embed(
            title=":gun:ロシアンルーレット:bangbang:",
            description="ボタンを押してルーレットを回そう:exclamation:",
            color=discord.Color.dark_purple()
        )
        view = discord.ui.View()
        button = discord.ui.Button(label="スピン", style=discord.ButtonStyle.primary)

        # games
        games = dict()
        game_id = interaction.channel_id
        games[game_id] = {'turns': 0, 'chamber': random.randint(1, 6)}

        # res
        res = ["セーフ:exclamation:", "バン:exclamation: YOU ARE DEAD:skull:"]

        async def button_callback(interaction: discord.Interaction):
            result = random.choice(res)
            if res.index(result) == 0:
                await update_bal_delta(bet_amount*self.GAMBLE_RATES["russian_roulette"], user_name)
            await interaction.response.send_message(f"{interaction.user.mention} {result}")
    
        button.callback = button_callback
        view.add_item(button)
        
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name=ALL_COMMANDS.gamble.rl_multi.name, description=ALL_COMMANDS.gamble.rl_multi.description)
    @app_commands.describe(
        pocket=ALL_COMMANDS.gamble.rl_multi.pocket
    )
    async def rl_multi(self, interaction:discord.Interaction, pocket:str):
        # user in question
        user = interaction.user
        user_name = user.name
        # check bet_amount, and get reply message [str | embed] and bet_amout [int]
        bet_amount_check_response, pocket = await check_bet_amount(
            bet_amount=pocket, 
            user=user, 
            game_name="ロシアンルーレット"
            )
        if isinstance(bet_amount_check_response, str):
            await interaction.response.send_message(bet_amount_check_response)
        elif isinstance(bet_amount_check_response, discord.Embed):
            await interaction.response.send_message(embed=bet_amount_check_response)
        else:
            print(f"invalid return of {type(bet_amount_check_response)}")
            return
        
        if pocket is None: return
        
        # get players to join
        embed = discord.Embed(
            title=":yen:ロシアンルーレット:yen:",
            description=f"{user.mention}がロシアンルーレットの部屋を立てました:bangbang:\n:gun:でリアクションして参加しよう！\n生き延びた人が全額もらえるよ！",
            color=discord.Color.yellow()
        )
        embed.add_field(name="参加費用", value=f"{clean_money_display(pocket)}")
        # discord.WebhookMessage
        webhook_msg = await interaction.followup.send(embed=embed, wait=True)
        # get discord.Message obj
        msg = await webhook_msg.fetch()
        # add reaction for other players to click
        await webhook_msg.add_reaction("🔫")
        # wait for users to react
        await asyncio.sleep(10)

        def check(reaction, user):
            return str(reaction.emoji) == "🔫" and user != self.bot.user
        
        # get msg in cache
        cache_msg = discord.utils.get(self.bot.cached_messages, id=msg.id)
        reactions = cache_msg.reactions

        # scan reactions on embed. check which user would like to participate
        for r in reactions:
            if str(r.emoji) == "🔫":
                async for u in r.users():
                    if u != self.bot.user and u not in self.rl_multi_participants:
                        self.rl_multi_participants.append(u)
        
        # if there is only 1 user, silently add bot to user list
        if len(self.rl_multi_participants) < 2:
            self.rl_multi_participants.append(self.bot.user)

        # participant count
        num_players = len(self.rl_multi_participants)

        data = await read_json("gamble")

        # display users in-game
        embed = discord.Embed(
            title=f"🎉{user.name}様主催のロシアンルーレット:exclamation:\n参加者はこちら:exclamation:",
            color=discord.Color.purple()
        )
        for u in self.rl_multi_participants:
            embed.add_field(name=f"", value=f"{u.mention}\n財力は{clean_money_display(data[u.name])}")
        await interaction.followup.send(embed = embed)

        # gameplay
        while len(self.rl_multi_participants) > 1:
            p = random.choice(self.rl_multi_participants)
            await update_bal_delta(-pocket, p.name)
            self.rl_multi_participants.remove(p)
            await interaction.followup.send(f":skull:{p.mention}:gun:は死にました...")
            await asyncio.sleep(3)
        
        # last man standing
        winner = self.rl_multi_participants[0]
        win_amount = pocket * num_players
        await update_bal_delta(win_amount, winner.name)
        await interaction.followup.send(f":tada:{winner.mention}:tada:の勝利:exclamation:\n賞金{clean_money_display(win_amount)}ゲット:bangbang:")

async def setup(bot):
    await bot.add_cog(GambleCog(bot), guilds=[discord.Object(id=get_guild_id())])