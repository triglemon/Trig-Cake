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
        steam_game = SteamApp(appid, self.bot)
        await steam_game.parse_news()
        steam_game.fetch_update()
        discord_post = discord.Embed(title=steam_game.name,
                                     description=steam_game.found_news)
        await self.bot.say(embed=discord_post)

    @commands.command(name='last')
    @commands.is_owner()
    async def last(self, appid):
        """Gets last announcement from json"""
        steam_game = SteamApp(appid, self.bot)
        steam_game.fetch_update()
        steam_game.fetch_name()
        discord_post = discord.Embed(title=steam_game.name,
                                     description=steam_game.last_news)
        await self.bot.say(embed=discord_post)

    @commands.command(name='purge')
    @commands.is_owner()
    async def purge_channel(self, ctx):
        """Purges testing channel only"""
        channel = self.bot.get_channel(466807163323416588)
        await channel.purge(limit=100)
        await ctx.send("Purged!")


def setup(bot):
    bot.add_cog(Debug(bot))
