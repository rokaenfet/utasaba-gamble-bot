import discord
from discord.ext import commands
from discord import app_commands
from funcs import *
from commands_argument import CommandArg


class NameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # activate on this cog(class) of commands being successfully loaded
    @commands.Cog.listener()
    async def on_ready(self):
        t = time.time()

    # Sample command on how to make a slash command on discord.py in cog.py
    """
    @app_commands.command decorator is a MUST NEED. this defines it as a / command
    @app_commands.describe helps the user know what each parameter is for
    command func
        ensure command func is asynchronous
        name of command (here its sample) will be the command name -> /sample [must_need_param] (optional_param)
        the first 2 parameters will always be (self, interaction:discord.Interaction)
            see discord.py API for discord.Interaction usage
        make sure to add typing (restriction parameter input data types) for each parameter other than self
        Bot MUST need to reply to message using interaction.response.send_message()
            any following messages from the bot must be sent via interaction.followup.send()
            if a message doesn't get sent for 3 ~ 5 secs, use interaction.response.defer()
    """
    @app_commands.command(name="sample", description="hello world")
    @app_commands.describe(
        must_need_param = "description of param that must be filled for command to be used",
        optional_param = "description of param that is optional when using command"
    )
    async def sample(self, interaction:discord.Interaction, must_need_param:discord.Member, optional_param:int = 0):
        await interaction.response.send_message("hello world")


# Sync cog to the guild, add to command tree
async def setup(bot):
    await bot.add_cog(NameCog(bot), guilds=[discord.Object(id=get_guild_id())])