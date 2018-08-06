from discord.ext import commands
from SteamApp import SteamApp


class Debug:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def found(self, url):
        stm = SteamApp(url, self.client)
        await stm.acquire()
        await stm.parse()
        await self.client.say(stm.found)

    @commands.command()
    async def last(self, url):
        stm = SteamApp(url, self.client)
        stm.fetchupdate()
        await self.client.say(stm.last)


def setup(client):
    client.add_cog(Debug(client))
