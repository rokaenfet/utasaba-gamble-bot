import discord
from funcs import *
from discord.ext import commands
from discord import app_commands
import os

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")}')
        await self.bot.tree.sync(guild=discord.Object(get_guild_id()))

    @app_commands.command(name="info", description="display various information")
    async def info(self, interaction:discord.Interaction):
        embed = discord.Embed(title=":info: _Info_", color=discord.Color.gold())
        embed.add_field(name="Author", value=f"{interaction.user}", inline=False)
        embed.add_field(name="Locale", value=f"{interaction.locale}", inline=False)
        embed.add_field(name="Guild Locale", value=f"{interaction.guild_locale}", inline=False)
        embed.add_field(name="Client", value=f"{interaction.client}", inline=False)
        embed.add_field(name="Command Called", value=f"{interaction.command}", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(BasicCog(bot))