from discord.ext import commands
from SteamApp import SteamApp


class Last:
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def last(self, url):
        stm = SteamApp(url, self.client)
        stm.fetchjson()
        await self.client.say(stm.last)


def setup(client):
    client.add_cog(Last(client))
