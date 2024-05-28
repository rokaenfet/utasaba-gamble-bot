import discord
import os
from discord.ext import commands
from discord import app_commands
from funcs import *

class MemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")}')
        await self.bot.tree.sync(guild=discord.Object(get_guild_id()))

async def setup(bot):
    await bot.add_cog(MemberCog(bot))