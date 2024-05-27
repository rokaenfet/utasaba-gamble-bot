from discord.ext import commands

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="info")
    async def info(self, ctx):
        """
        !info
        guild
        author
        message.id
        """
        await ctx.reply(f"guild: {ctx.guild}\nauthor: {ctx.author}\nsender: {ctx.message.id}")

async def setup(bot):
    await bot.add_cog(BasicCog(bot))