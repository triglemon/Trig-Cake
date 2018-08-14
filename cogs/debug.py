from discord.ext import commands
from modules.steamapp import SteamApp
import discord
import datetime


class Debug:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='found')
    @commands.is_owner()
    async def found(self, appid):
        stm = SteamApp(appid, self.bot)
        await stm.parse()
        stm.fetchupdate()
        embed = discord.Embed(title=stm.name, description=stm.found)
        await self.bot.say(embed=embed)

    @commands.command(name='last')
    @commands.is_owner()
    async def last(self, appid):
        stm = SteamApp(appid, self.bot)
        stm.fetchupdate()
        stm.fetchname()
        embed = discord.Embed(title=stm.name, description=stm.last)
        await self.bot.say(embed=embed)

    @commands.command(name='purge')
    @commands.is_owner()
    async def purgechannel(self, ctx):
        channel = self.bot.get_channel(466807163323416588)
        await channel.purge(limit=100)
        await ctx.send("Purged!")


def setup(bot):
    bot.add_cog(Debug(bot))
