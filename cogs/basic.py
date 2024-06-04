import discord
import os
import time
import typing
from funcs import *
from commands_argument import CommandArg
from discord.ext import commands
from discord import app_commands

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

    @app_commands.command(name="info", description="display various information")
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

    @app_commands.command(name="avatar", description="Get user avatar")
    @app_commands.describe(
        member="@[ユーザー名]"
    )
    async def avatar(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.send_message(member.display_avatar)

    @app_commands.command(name="daily", description="１日一回のデイリー報酬をもらうコマンド")
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
            delta_time = user_last_daily_time+datetime.timedelta(days=1)
            await interaction.response.send_message(embed = discord.Embed(
                title=":x: デイリーはまだ受け取れないよ :x:",
                description=f"{user.mention}の現在の**ストリークは**{streak}連です！\n次のデイリー報酬は{delta_time.time()}後に受け取れるよ:exclamation:",
                color=discord.Color.teal()
            ))

async def setup(bot):
    await bot.add_cog(BasicCog(bot), guilds=[discord.Object(id=get_guild_id())])