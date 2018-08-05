from discord.ext import commands
from SteamApp import SteamApp


class Found:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def found(self, url):
        stm = SteamApp(url, self.client)
        await stm.acquire()
        await stm.parse()
        await self.client.say(stm.found)


def setup(client):
    client.add_cog(Found(client))
