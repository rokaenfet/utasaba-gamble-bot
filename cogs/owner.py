from discord.ext import commands
from funcs import *

class OwnerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

    @commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, ctx):
        extensions = get_extensions()
        load_success = True
        for ext in extensions:
            try:
                await self.bot.reload_extension(f"cogs.{ext}")
                await ctx.reply(f'...{ext} successfully reloaded')
            except:
                load_success = False
                await ctx.reply(f'...{ext} failed to load')
        if load_success:
            embed = discord.Embed(title="Reload", description=f"Load Success :D", color=discord.Color.brand_green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Reload", description=f"Load Failed :/", color=discord.Color.dark_red())
            await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        pass

async def setup(bot):
    await bot.add_cog(OwnerCog(bot))