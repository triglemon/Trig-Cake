from discord.ext import commands
from modules.steamapp import SteamApp
import discord


class Debug:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def found(self, url):
        stm = SteamApp(url, self.client)
        await stm.acquire()
        await stm.parse()
        embed = discord.Embed(title=stm.name, description=stm.found)
        await self.client.say(embed=embed)

    @commands.command()
    async def last(self, url):
        stm = SteamApp(url, self.client)
        stm.fetchupdate()
        await stm.acquire()
        embed = discord.Embed(title=stm.name, description=stm.last)
        await self.client.say(embed=embed)


def setup(client):
    client.add_cog(Debug(client))
