import discord
import time
import requests
import random
from funcs import *
from get_gifs import Gifs
from discord.ext import commands
from discord import app_commands
from commands_argument import get_all_commands

ALL_COMMANDS = get_all_commands()

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DAILY_REWARD = 1000
        # load gif
        self.gif = Gifs()
        self.gif.load_gifs()
        
    @commands.Cog.listener()
    async def on_ready(self):
        pass

    @app_commands.command(name=ALL_COMMANDS.basic.info.name, description=ALL_COMMANDS.basic.info.description)
    async def info(self, interaction:discord.Interaction):
        try:
            embed = discord.Embed(title=":information_source: Info", color=discord.Color.gold())
            embed.add_field(name="Author", value=f"{interaction.user}", inline=False)
            embed.add_field(name="Locale", value=f"{interaction.locale}", inline=False)
            embed.add_field(name="Guild Locale", value=f"{interaction.guild_locale}", inline=False)
            embed.add_field(name="Client", value=f"{interaction.client.user}", inline=False)
            embed.add_field(name="/info command description", value=f"{interaction.command.description}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error: {e}")

    @app_commands.command(name=ALL_COMMANDS.basic.avatar.name, description=ALL_COMMANDS.basic.avatar.description)
    @app_commands.describe(
        member=ALL_COMMANDS.basic.avatar.member
    )
    async def avatar(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.send_message(member.display_avatar, ephemeral=True)

    @app_commands.command(name=ALL_COMMANDS.basic.daily.name, description=ALL_COMMANDS.basic.daily.description)
    async def daily(self, interaction:discord.Interaction):
        # user
        user = interaction.user
        user_name = user.name

        # time in UTC
        cur_time = datetime.datetime.now(datetime.timezone.utc)
        fortnite_time = cur_time - datetime.timedelta(days=2)

        # check daily data
        daily_data = await read_json("daily")

        # if daily_data has never been initialized
        if daily_data is None: daily_data = {}
        # is user in daily
        if user_name not in daily_data:
            daily_data[user_name] = {
                "streak":0,
                "last_daily": encode_datetime_timestamp(fortnite_time)
            }
            update_json("daily", daily_data)

        user_daily_data = daily_data[user_name]

        # if its been more than a day, allow daily
        user_last_daily_time = decode_datetime_timestamp(user_daily_data["last_daily"])
        delta_time = cur_time - user_last_daily_time
        can_get_daily = delta_time.days >= 1

        # reset streak if 2 days has passed
        if delta_time.days >= 2:
            streak = 0
        else:
            streak = user_daily_data["streak"]
        
        # responses
        if can_get_daily:
            # add streak
            streak += 1
            # add money
            await update_bal_delta(amount = self.DAILY_REWARD, user = user_name)
            await interaction.response.send_message(embed = discord.Embed(
                title=":calendar_spiral:デイリー報酬ゲット:exclamation:",
                description=f"{user.mention}は{clean_money_display(int(self.DAILY_REWARD*(1.2**(streak-1))))}をもらいました！\n現在のストリークは{streak}連です！",
                color=discord.Color.teal()
            ))
            # update json w new streak and timestamp
            daily_data[user_name] = {
                "streak":streak, 
                "last_daily": encode_datetime_timestamp(cur_time)
                }
            update_json("daily", daily_data)
        else:
            next_daily = (user_last_daily_time+datetime.timedelta(days=1)) - cur_time
            hour, minute, second = next_daily.seconds//3600, (next_daily.seconds//60)%60, next_daily.seconds%60
            await interaction.response.send_message(embed = discord.Embed(
                title=":x: デイリーはまだ受け取れないよ :x:",
                description=f"{user.mention}の現在の**ストリークは**{streak}連です！\n次のデイリー報酬は{hour}:{minute}:{second}後に受け取れるよ:exclamation:",
                color=discord.Color.teal()
            ))

    @app_commands.command(name=ALL_COMMANDS.basic.send_money.name, description=ALL_COMMANDS.basic.send_money.description)
    @app_commands.describe(
        user=ALL_COMMANDS.basic.send_money.user,
        amount=ALL_COMMANDS.basic.send_money.amount
    )
    async def send_money(self, interaction:discord.Interaction, user:discord.Member, amount:str):
        COMMISION = 0.05
        # user
        send_user = interaction.user
        send_user_name = send_user.name
        receive_user = user
        receive_user_name = receive_user.name
        # data
        data = await read_json("gamble")
        # check if "amount" is all
        if isinstance(amount, str):
            if amount == "all":
                amount = data[send_user_name]
            else:
                try:
                    amount = int(amount)
                except:
                    await interaction.response.send_message(f":x: 数字か「all」を入力してくださいね")
                    return
        # check amount is legal
        if 0 > amount:
            await interaction.response.send_message(f":x: {send_user.mention}0以上の金額を入力してください")
            return
        if amount > data[send_user_name]:
            await interaction.response.send_message(f":x: {send_user.mention}様の残高は{clean_money_display(data[send_user_name])}です。この残高以内の金額をしてしてください:exclamation:")
            return
        # transfer money
        await update_bal_delta(-amount, send_user_name)
        await update_bal_delta(int(amount*(1-COMMISION)), receive_user_name)
        # response
        await interaction.response.send_message(embed=discord.Embed(
            title=":ballot_box_with_check:送金完了:exclamation:",
            description=f"{send_user.mention}は{receive_user.mention}に{clean_money_display(int(amount-amount*COMMISION))}送金しました。\n手数料は{clean_money_display(int(amount*COMMISION))}です",
            color=discord.Color.blue()
        ))

    @app_commands.command(name=ALL_COMMANDS.basic.slap.name, description=ALL_COMMANDS.basic.slap.description)
    @app_commands.describe(
        user=ALL_COMMANDS.basic.slap.user
    )
    async def slap(self, interaction:discord.Interaction, user:discord.Member):
        # If user A slaps B. quantity of slaps is accessed via read_json("slap_interaction.json")[A][B]
        # pre vars
        interaction_name = "slap"
        json_f = f"{interaction_name}_interaction"
        data = await read_json(json_f)
        # user
        send_user = interaction.user
        send_user_name = send_user.name
        receive_user = user
        receive_user_name = receive_user.name

        gif_url = await basic_interaction(
            interaction=interaction,
            user=user,
            gifs=self.gif.gifs[interaction_name],
            json_f=json_f
        )

        data = await read_json(json_f)
        embed = discord.Embed(
            title=":raised_hand:ビ・ン・タ:raised_back_of_hand:",
            description=f"{send_user.mention}は{receive_user.mention}を**{data[send_user_name][receive_user_name]}回**ビンタしました:exclamation:",
            color=discord.Color.purple()
        )
        interaction_quantity = data[send_user_name][receive_user_name]
        if interaction_quantity % 10 == 0:
            embed.add_field(name=f"{interaction_quantity}回目:exclamation:",value=f"報酬に{clean_money_display(interaction_quantity*100)}")
        
        embed.set_image(url=gif_url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=ALL_COMMANDS.basic.punch.name, description=ALL_COMMANDS.basic.punch.description)
    @app_commands.describe(
        user=ALL_COMMANDS.basic.punch.user
    )
    async def punch(self, interaction:discord.Interaction, user:discord.Member):
        # If user A punch B. quantity of punch is accessed via read_json("punch_interaction.json")[A][B]
        # pre vars
        interaction_name = "punch"
        json_f = f"{interaction_name}_interaction"
        data = await read_json(json_f)
        # user
        send_user = interaction.user
        send_user_name = send_user.name
        receive_user = user
        receive_user_name = receive_user.name

        gif_url = await basic_interaction(
            interaction=interaction,
            user=user,
            gifs=self.gif.gifs[interaction_name],
            json_f=json_f
        )
        data = await read_json(json_f)
        embed = discord.Embed(
            title=":left_facing_fist:パ・ン・チ:right_facing_fist:",
            description=f"{send_user.mention}は{receive_user.mention}を**{data[send_user_name][receive_user_name]}回**パンチしました:exclamation:",
            color=discord.Color.purple()
        )
        interaction_quantity = data[send_user_name][receive_user_name]
        if interaction_quantity % 10 == 0:
            embed.add_field(name=f"{interaction_quantity}回目:exclamation:",value=f"報酬に{clean_money_display(interaction_quantity*100)}")
        
        embed.set_image(url=gif_url)
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name=ALL_COMMANDS.basic.dance.name, description=ALL_COMMANDS.basic.dance.description)
    @app_commands.describe(
        user=ALL_COMMANDS.basic.dance.user
    )
    async def dance(self, interaction:discord.Interaction, user:discord.Member):
        # If user A dance B. quantity of dance is accessed via read_json("dance_interaction.json")[A][B]
        # pre vars
        interaction_name = "dance"
        json_f = f"{interaction_name}_interaction"
        data = await read_json(json_f)
        # user
        send_user = interaction.user
        send_user_name = send_user.name
        receive_user = user
        receive_user_name = receive_user.name

        gif_url = await basic_interaction(
            interaction=interaction,
            user=user,
            gifs=self.gif.gifs[interaction_name],
            json_f=json_f
        )
        data = await read_json(json_f)
        embed = discord.Embed(
            title=":dancer:ダンシング:musical_note::man_dancing:",
            description=f"{send_user.mention}は{receive_user.mention}と**{data[send_user_name][receive_user_name]}回**踊りました:exclamation:",
            color=discord.Color.purple()
        )
        interaction_quantity = data[send_user_name][receive_user_name]
        if interaction_quantity % 10 == 0:
            embed.add_field(name=f"{interaction_quantity}回目:exclamation:",value=f"報酬に{clean_money_display(interaction_quantity*100)}")
        
        embed.set_image(url=gif_url)
        
        await interaction.response.send_message(embed=embed)
        

    @app_commands.command(name=ALL_COMMANDS.basic.hug.name, description=ALL_COMMANDS.basic.hug.description)
    @app_commands.describe(
        user=ALL_COMMANDS.basic.hug.user
    )
    async def hug(self, interaction:discord.Interaction, user:discord.Member):
        # If user A hug B. quantity of hug is accessed via read_json("hug_interaction.json")[A][B]
        # pre vars
        interaction_name = "hug"
        json_f = f"{interaction_name}_interaction"
        data = await read_json(json_f)
        # user
        send_user = interaction.user
        send_user_name = send_user.name
        receive_user = user
        receive_user_name = receive_user.name

        gif_url = await basic_interaction(
            interaction=interaction,
            user=user,
            gifs=self.gif.gifs[interaction_name],
            json_f=json_f
        )
        data = await read_json(json_f)
        embed = discord.Embed(
            title=":people_hugging:はぐぅぅぅ:people_hugging:",
            description=f"{send_user.mention}は{receive_user.mention}を**{data[send_user_name][receive_user_name]}回**ハグしました:exclamation:",
            color=discord.Color.purple()
        )
        interaction_quantity = data[send_user_name][receive_user_name]
        if interaction_quantity % 10 == 0:
            embed.add_field(name=f"{interaction_quantity}回目:exclamation:",value=f"報酬に{clean_money_display(interaction_quantity*100)}")
        
        embed.set_image(url=gif_url)
        
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name=ALL_COMMANDS.basic.reload_gif.name, description=ALL_COMMANDS.basic.reload_gif.description)
    async def reload_gif(self, interaction:discord.Interaction):
        t = time.time()
        self.gif.load_gifs()
        await interaction.response.send_message(f"Reloaded gifs in {round(time.time()-t,3)}s")

    @app_commands.command(name=ALL_COMMANDS.basic.rankings.name, description=ALL_COMMANDS.basic.rankings.description)
    async def rankings(self, interaction:discord.Interaction, name:str):
        pass

async def setup(bot):
    await bot.add_cog(BasicCog(bot), guilds=[discord.Object(id=get_guild_id())])