import discord
import os
import time
import typing
from funcs import *
from discord.ext import commands
from discord import app_commands
from commands_argument import get_all_commands

ALL_COMMANDS = get_all_commands()

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DAILY_REWARD = 1000
        
    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

    @app_commands.command(name=ALL_COMMANDS.basic.info.name, description=ALL_COMMANDS.basic.info.description)
    async def info(self, interaction:discord.Interaction):
        try:
            embed = discord.Embed(title=":information_source: Info", color=discord.Color.gold())
            embed.add_field(name="Author", value=f"{interaction.user}", inline=False)
            embed.add_field(name="Locale", value=f"{interaction.locale}", inline=False)
            embed.add_field(name="Guild Locale", value=f"{interaction.guild_locale}", inline=False)
            embed.add_field(name="Client", value=f"{interaction.client.user}", inline=False)
            embed.add_field(name="/info command description", value=f"{interaction.command.description}", inline=False)
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(f"Error: {e}")

    @app_commands.command(name=ALL_COMMANDS.basic.avatar.name, description=ALL_COMMANDS.basic.avatar.description)
    @app_commands.describe(
        member=ALL_COMMANDS.basic.avatar.member
    )
    async def avatar(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.send_message(member.display_avatar)

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
            await update_json("daily", daily_data)
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

        


async def setup(bot):
    await bot.add_cog(BasicCog(bot), guilds=[discord.Object(id=get_guild_id())])