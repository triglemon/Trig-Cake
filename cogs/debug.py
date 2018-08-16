"""
This module contains commands for testing/debugging purposes.
Mostly obselete.
"""
import discord
from discord.ext import commands
from modules.steamapp import SteamApp


class Debug:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='found')
    @commands.is_owner()
    async def found(self, appid):
        """Finds newest announcement"""
        stm = SteamApp(appid, self.bot)
        await stm.parse_news()
        stm.fetch_update()
        embed = discord.Embed(title=stm.name, description=stm.found_news)
        await self.bot.say(embed=embed)

    @commands.command(name='last')
    @commands.is_owner()
    async def last(self, appid):
        """Gets last announcement from json"""
        stm = SteamApp(appid, self.bot)
        stm.fetch_update()
        stm.fetch_name()
        embed = discord.Embed(title=stm.name, description=stm.last_news)
        await self.bot.say(embed=embed)

    @commands.command(name='purge')
    @commands.is_owner()
    async def purge_channel(self, ctx):
        """Purges testing channel only"""
        channel = self.bot.get_channel(466807163323416588)
        await channel.purge(limit=100)
        await ctx.send("Purged!")


def setup(bot):
    bot.add_cog(Debug(bot))
