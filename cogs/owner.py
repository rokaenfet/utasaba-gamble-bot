from discord.ext import commands
from discord import app_commands
from funcs import *
import os
import time
import datetime

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

    @app_commands.command(name="admin_change_money", description="ADMIN: change bal of user")
    @app_commands.describe(
        user="残高を変更する対象の@[ユーザー名]",
        money="変更後の残高となる金額"
    )
    @commands.is_owner()
    async def admin_change_money(self, interaction:discord.Interaction, user:discord.Member = None, money:int = None):
        gamble_data = await read_json("gamble")
        if user is None:
            user = interaction.user
        else:
            user = user
        user_name = user.name
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

    @app_commands.command(name="reload", description="update cogs/*** extensions")
    @commands.is_owner()
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

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        pass

async def setup(bot):
    await bot.add_cog(OwnerCog(bot), guilds=[discord.Object(id=get_guild_id())])