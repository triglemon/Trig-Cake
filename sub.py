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
                embed = discord.Embed(title=url, description="Not a valid URL.",
                                      color=0xebbe23)
                await self.client.say(embed=embed)
            else:
                storepage = await tryget(url)
                storesoup = Soup(storepage, 'html.parser')
                metatag = storesoup.find('meta', {'property': 'og:url'})
                urlcheck = metatag['content']
                if urlcheck == 'https://store.steampowered.com/':
                    embed = discord.Embed(title=url, description="Game does not exist.",
                                          color=0xebbe23)
                    await self.client.say(embed=embed)
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
                        embed = discord.Embed(title=url, description="Channel is already subscribed to game.",
                                              color=0xebbe23)
                        await self.client.say(embed=embed)
                    else:
                        steamdict[url].append(channelid)
                        with open('steam.json', 'w') as newsteam:
                            json.dump(steamdict, newsteam)
                        gamename = storesoup.find('div', {'class': 'apphub_AppName'}).text
                        embed = discord.Embed(title=url, description=f"Channel is now subscribed to {gamename}!",
                                              color=0xebbe23)
                        await self.client.say(embed=embed)

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

                        embed = discord.Embed(title=url, description="Channel is now unsubscribed from that game.",
                                              color=0xebbe23)
                        await self.client.say(embed=embed)
                else:
                    embed = discord.Embed(title=url, description="Channel is not subscribed to that game.",
                                          color=0xebbe23)
                    await self.client.say(embed=embed)
            else:
                embed = discord.Embed(title=url, description="Channel is not subscribed to that game.",
                                      color=0xebbe23)
                await self.client.say(embed=embed)

    @commands.command(pass_context=True)
    async def subbed(self, ctx):
        channelid = ctx.message.channel.id
        with open('steam.json') as steam:
            steamdict = json.load(steam)
        subbedlist = [url for url in steamdict if channelid in steamdict[url]]
        if len(subbedlist) == 0:
            embed = discord.Embed(title="!cakesubbed",
                                  description="Channel is not subscribed to any games.",
                                  color=0xebbe23)
            await self.client.say(embed=embed)
        else:
            message = ''
            for url in subbedlist:
                stm = SteamApp(url, self.client)
                await stm.acquire()
                message += (stm.name + ', ')
            message = message[:-3] + '.'
            embed = discord.Embed(title="This channel is subbed to:", description=message,
                                  color=0xebbe23)
            await self.client.say(embed=embed)

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
            embed = discord.Embed(title=f"{stm.name} is not on sale right now!", description="Better luck next time!",
                                  color=0xebbe23)
            await self.client.say(embed=embed)


def setup(client):
    client.add_cog(Sub(client))
