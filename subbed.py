from discord.ext import commands
import json
from tryget import tryget
from bs4 import BeautifulSoup as Soup


class Subbed:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def subbed(self, ctx):
        channelid = ctx.message.channel.id
        with open('steam.json') as steam:
            steamdict = json.load(steam)
        subbedlist = [url for url in steamdict if channelid in steamdict[url]]
        if len(subbedlist) == 0:
            await self.client.say("Channel is not subscribed to any games.")
        else:
            message = "This channel is subbed to:  "
            for url in subbedlist:
                storepage = await tryget(url)
                storesoup = Soup(storepage, 'html.parser')
                gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                message += (gamename + ',  ')
            message = message[:-3] + '.'
            await self.client.say(message)


def setup(client):
    client.add_cog(Subbed(client))
