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

    @commands.command(pass_context=True)
    async def unsub(self, ctx, link):
        if ctx.message.author.server_permissions.administrator:
            url = link
            channelid = ctx.message.channel.id
            with open('steam.json') as steam:
                steamdict = json.load(steam)
            if url in steamdict:
                if channelid in steamdict[url]:
                    steamdict[url].remove(channelid)
                    if len(steamdict[url]) == 0:
                        del steamdict[url]
                        with open('updates.json') as updates:
                            updatesdict = json.load(updates)
                        del updatesdict[url]
                        with open('updates.json', 'w') as newupdates:
                            json.dump(updatesdict, newupdates)
                    with open('steam.json', 'w') as newsteam:
                        json.dump(steamdict, newsteam)

                        await self.client.say("Channel is now unsubscribed from that game.")
                else:
                    await self.client.say("Channel is not subscribed to that game.")
            else:
                await self.client.say("Channel is not subscribed to that game.")


def setup(client):
    client.add_cog(Sub(client))
