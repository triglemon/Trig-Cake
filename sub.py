from discord.ext import commands
from tryget import tryget
from SteamApp import SteamApp
import json
from bs4 import BeautifulSoup as Soup


class Sub:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def sub(self, ctx, link):
        if ctx.message.author.server_permissions.administrator:
            channelid = ctx.message.channel.id
            url = link
            prefix = 'https://store.steampowered.com/app/'
            if prefix not in url:
                await self.client.say("Not a valid url.")
            else:
                storepage = await tryget(url)
                storesoup = Soup(storepage, 'html.parser')
                metatag = storesoup.find('meta', {'property': 'og:url'})
                urlcheck = metatag['content']
                if urlcheck == 'https://store.steampowered.com/':
                    await self.client.say("Game does not exist.")
                else:
                    with open('steam.json') as steam:
                        steamdict = json.load(steam)
                    if url not in steamdict:
                        steamdict[url] = []
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        newgame = SteamApp(url, self.client)
                        await newgame.acquire()
                        await newgame.parse()
                        with open('updates.json') as updates:
                            updatesdict = json.load(updates)
                        updatesdict[newgame.url] = newgame.found
                        with open('updates.json', 'w') as newupdates:
                            json.dump(updatesdict, newupdates)
                    if channelid in steamdict[url]:
                        await self.client.say("Channel is already subscribed to game.")
                    else:
                        steamdict[url].append(channelid)
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                        await self.client.say(f"Channel is now subscribed to {gamename}!")


def setup(client):
    client.add_cog(Sub(client))
