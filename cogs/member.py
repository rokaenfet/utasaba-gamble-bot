import discord
import os
import time
from discord.ext import commands
from discord import app_commands
from funcs import *

class MemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

async def setup(bot):
    await bot.add_cog(MemberCog(bot), guilds=[discord.Object(id=get_guild_id())])