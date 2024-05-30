import discord
import os
import time
from funcs import *
from discord.ext import commands
from discord import app_commands

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
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
    async def avatar(self, interaction:discord.Interaction, member:discord.Member):
        await interaction.response.send_message(member.display_avatar)

async def setup(bot):
    await bot.add_cog(BasicCog(bot), guilds=[discord.Object(id=get_guild_id())])