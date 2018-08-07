from discord.ext import commands
from tryget import tryget
from steamapp import SteamApp
import json
from bs4 import BeautifulSoup as Soup
import discord


class Sub:
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    async def sub(self, ctx, link):
        if ctx.message.author.server_permissions.administrator:
            channelid = ctx.message.channel.id
            url = link
            if 'https://store.steampowered.com/app/' not in url:
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
                        newgame.gaben()
                        with open('update.json') as update:
                            updatedict = json.load(update)
                        updatedict[newgame.url] = newgame.found
                        with open('update.json', 'w') as newupdate:
                            json.dump(updatedict, newupdate)
                        with open('sale.json') as sale:
                            saledict = json.load(sale)
                        saledict[newgame.url] = newgame.foundsale
                        with open('sale.json', 'w') as newsale:
                            json.dump(saledict, newsale)
                    if channelid in steamdict[url]:
                        await self.client.say("Channel is already subscribed to game.")
                    else:
                        steamdict[url].append(channelid)
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                        await self.client.say(f"Channel is now subscribed to {gamename}!")

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
                        with open('update.json') as update:
                            updatedict = json.load(update)
                        del updatedict[url]
                        with open('update.json', 'w') as newupdate:
                            json.dump(updatedict, newupdate)
                        with open('sale.json') as sale:
                            saledict = json.load(sale)
                        del saledict[url]
                        with open('sale.json', 'w') as newsale:
                            json.dump(saledict, newsale)
                    with open('steam.json', 'w') as newsteam:
                        json.dump(steamdict, newsteam)

                        await self.client.say("Channel is now unsubscribed from that game.")
                else:
                    await self.client.say("Channel is not subscribed to that game.")
            else:
                await self.client.say("Channel is not subscribed to that game.")

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
                stm = SteamApp(url, self.client)
                await stm.acquire()
                message += (stm.name + ',  ')
            message = message[:-3] + '.'
            await self.client.say(message)

    @commands.command()
    async def sale(self, link):
        stm = SteamApp(link, self.client)
        await stm.acquire()
        await stm.parse()
        stm.gaben()
        if stm.foundsale:
            embed = discord.Embed(title=stm.name, url=stm.url, description=stm.saledesc,
                                  color=0xebbe23)
            embed.set_footer(text="Github repo: https://github.com/triglemon/Trig-Cake")
            embed.set_image(url=stm.thumbnail)
            await self.client.say(embed=embed)
        else:
            message = f"Bah humbug, {stm.name} is not on sale right now! Better luck next time!"
            await self.client.say(message)


def setup(client):
    client.add_cog(Sub(client))
