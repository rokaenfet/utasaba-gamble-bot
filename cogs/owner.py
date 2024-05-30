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

    @commands.command()
    async def admin_get_num_inp(self, ctx):
        await ctx.reply("how much to change？")
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        try:
            res = await self.bot.wait_for("message", check=check, timeout=5)
            msg = res.content
            if check_is_num(msg):
                return int(msg)
            else:
                return False
        except asyncio.TimeoutError:
            return False

    @commands.command()
    @commands.is_owner()
    async def admin_change_money(self, ctx):
        gamble_data = read_json("gamble")
        user = ctx.author.name
        num = await ctx.invoke(self.bot.get_command("admin_get_num_inp"))
        if not num:
            return
        await ctx.reply(f"changing your bal from {gamble_data[user]} > {num}")
        update_bal(num, user)
        gamble_data = read_json("gamble")
        await ctx.reply(f"your new bal is {gamble_data[user]}")

    @commands.command(name="reload", description="update cogs/*** extensions")
    @commands.is_owner()
    async def reload(self, ctx):
        extensions = get_extensions()
        load_success = True
        #timestamp=datetime.now(datetime.timezone.utc
        embed_dict = {}
        await ctx.reply(embed=discord.Embed(title="Reloading Extensions...", color=discord.Color.dark_grey()))
        for ext in extensions:
            t = time.time()
            try:
                await self.bot.reload_extension(f"cogs.{ext}")
                # await ctx.reply(f'...{ext} successfully reloaded after {round(time.time()-t,3)}s')
                embed_dict[f"cogs.{ext}"] = [True, round(time.time()-t,3)]
                # embed.add_field(name=f":white_check_mark: cogs.{ext}", value=f"LOADED: {round(time.time()-t,3)}s", inline=False)
            except Exception as e:
                load_success = False
                # embed.add_field(name=f":sob: cogs.{ext}", value=f"LOAD FAILED: {round(time.time()-t,3)}s", inline=False)
                embed_dict[f"cogs.{ext}"] = [False, round(time.time()-t,3)]
                # await ctx.reply(f'...{ext} failed to load. Exception: {e}. Time taken: {round(time.time()-t,3)}s')

        # response embed
        embed = discord.Embed(
            title="Extensions Reloaded Success :D" if load_success else "Extensions Reload Failed :/", 
            color=discord.Color.brand_green() if load_success else discord.Color.dark_red()
            )
        for ext_name,(els, load_duration) in embed_dict.items():
            embed.add_field(
                name=f'{":white_check_mark:" if els else ":sob:"} cogs.{ext_name}', 
                value=f'LOAD {"SUCCESS" if els else "FAILED"}: {load_duration}s', inline=False)
        await ctx.reply(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        pass

async def setup(bot):
    await bot.add_cog(OwnerCog(bot), guilds=[discord.Object(id=get_guild_id())])