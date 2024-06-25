import discord
import os
import time
from discord.ext import commands
from discord import app_commands
from funcs import *
from commands_argument import get_all_commands

ALL_COMMANDS = get_all_commands()


class MemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()
        # print(f'Loading : cogs.{os.path.basename(__file__).replace(".py","")}')
        # await self.bot.tree.sync(guild=discord.Object(get_guild_id()))
        # print(f'Successfully loaded : cogs.{os.path.basename(__file__).replace(".py","")} in {round(time.time()-t,3)}s')

    @app_commands.command(name=ALL_COMMANDS.member.shiritori.name, description=ALL_COMMANDS.member.shiritori.description)
    async def shiritori(self, interaction:discord.Interaction):
        shiritori = await read_json("shiritori")
        await interaction.response.send_message(f"現在のしりとりの尻言葉は`{shiritori['history'][0]}`です")

async def setup(bot):
    await bot.add_cog(MemberCog(bot), guilds=[discord.Object(id=get_guild_id())])