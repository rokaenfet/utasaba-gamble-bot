from discord.ext import commands
from discord import app_commands
from funcs import *
import os
import time
import datetime
from commands_argument import get_all_commands

ALL_COMMANDS = get_all_commands()

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

    @app_commands.command(name=ALL_COMMANDS.owner.admin_change_money.name, description=ALL_COMMANDS.owner.admin_change_money.description)
    @app_commands.describe(
        user=ALL_COMMANDS.owner.admin_change_money.user,
        money=ALL_COMMANDS.owner.admin_change_money.money
    )
    @commands.has_role("Admin")
    async def admin_change_money(self, interaction:discord.Interaction, user:discord.Member = None, money:int = None):
        gamble_data = await read_json("gamble")
        if user is None:
            user = interaction.user
        else:
            user = user
        user_name = user.name
        gamble_data = await check_user_in_gamble_data(gamble_data, user_name)
        if money is None:
            money = gamble_data[user_name]
        prev_bal = gamble_data[user_name]
        await update_bal(money, user_name)
        gamble_data = await read_json("gamble")
        embed = discord.Embed(
            title=f":detective: ADMIN COMMAND", 
            description=f"Change Bal of {user.mention}\n:track_previous: prev bal :arrow_forward: {clean_money_display(prev_bal)} \n:track_next: new bal :arrow_forward: {clean_money_display(gamble_data[user_name])}",
            color=discord.Color.og_blurple())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name=ALL_COMMANDS.owner.reload.name, description=ALL_COMMANDS.owner.reload.description)
    @commands.has_role("Admin")
    async def reload(self, interaction:discord.Interaction):
        extensions = get_extensions()
        load_success = True
        #timestamp=datetime.now(datetime.timezone.utc
        embed_dict = {}
        await interaction.response.send_message(embed=discord.Embed(title="Reloading Extensions...", color=discord.Color.dark_grey()))
        for ext in extensions:
            t = time.time()
            try:
                await self.bot.reload_extension(f"cogs.{ext}")
                embed_dict[f"cogs.{ext}"] = [True, round(time.time()-t,3)]
            except Exception as e:
                load_success = False
                embed_dict[f"cogs.{ext}"] = [False, round(time.time()-t,3)]

        # response embed
        embed = discord.Embed(
            title="Extensions Reloaded Success :D" if load_success else "Extensions Reload Failed :/", 
            color=discord.Color.brand_green() if load_success else discord.Color.dark_red()
            )
        for ext_name,(els, load_duration) in embed_dict.items():
            embed.add_field(
                name=f'{":white_check_mark:" if els else ":sob:"} {ext_name}', 
                value=f'LOAD {"SUCCESS" if els else "FAILED"}: {load_duration}s', inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name=ALL_COMMANDS.owner.reset_daily.name, description=ALL_COMMANDS.owner.reset_daily.description)
    @app_commands.describe(
        user=ALL_COMMANDS.owner.reset_daily.user
    )
    @commands.has_role("Admin")
    async def reset_daily(self, interaction:discord.Interaction, user:discord.Member = None):
        # parse user arg
        if user is None:
            user = interaction.user
        else:
            user = user
        user_name = user.name
        # get daily.json
        daily_data = await read_json("daily")
        try:
            user_daily_data = daily_data[user_name]
        except:
            print(f"{user_name} has never received a daily reward. JSON does not exist")
        # set daily.json[user_name][last_daily] to yesterday
        daily_data[user_name]["last_daily"] = encode_datetime_timestamp(decode_datetime_timestamp(daily_data[user_name]["last_daily"]) - datetime.timedelta(days=1))
        update_json("daily", daily_data)
        await interaction.response.send_message(f"{user.mention} can now invoke `/daily` again")

    @app_commands.command(name=ALL_COMMANDS.owner.get_channel_text.name, description=ALL_COMMANDS.owner.get_channel_text.description)
    @app_commands.describe(
        channel=ALL_COMMANDS.owner.get_channel_text.channel,
        history=ALL_COMMANDS.owner.get_channel_text.history
    )
    @commands.has_role("Admin")
    async def get_channel_text(self, interaction:discord.Interaction, channel:discord.TextChannel, history:int=10):
        def format_rep(arr):
            s = ""
            for n in arr:
                s += f"\n{n}"
            print(s)
            return s
        messages = [message.content async for message in channel.history(limit=history+1)]
        try:
            await interaction.response.send_message(f"the **last {history} messages** on channel {channel.mention} is...{format_rep(messages)}")
        except:
            await interaction.response.send_message(f"history msg is too long")

    @app_commands.command(name=ALL_COMMANDS.owner.purge.name, description=ALL_COMMANDS.owner.purge.description)
    @app_commands.describe(
        channel = ALL_COMMANDS.owner.purge.channel,
        number  = ALL_COMMANDS.owner.purge.number
    )
    @commands.has_role("Admin")
    async def purge(self, interaction:discord.Interaction, channel:discord.TextChannel, number:int):
        num_messages = len([message async for message in channel.history(limit=100)])
        await interaction.response.defer()
        purged = await channel.purge(limit=min(num_messages, number))
        await interaction.followup.send(f"{min(num_messages,number)} messages has been purged from {channel.mention}")

async def setup(bot):
    await bot.add_cog(OwnerCog(bot), guilds=[discord.Object(id=get_guild_id())])