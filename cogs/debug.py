from discord.ext import commands
from modules.steamapp import SteamApp
import discord


class Debug:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def found(self, appid):
        stm = SteamApp(appid, self.bot)
        await stm.parse()
        stm.fetchupdate()
        embed = discord.Embed(title=stm.name, description=stm.found)
        await self.bot.say(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def last(self, appid):
        stm = SteamApp(appid, self.bot)
        stm.fetchupdate()
        stm.fetchname()
        embed = discord.Embed(title=stm.name, description=stm.last)
        await self.bot.say(embed=embed)


def setup(bot):
    bot.add_cog(Debug(bot))
