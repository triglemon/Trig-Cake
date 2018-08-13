import json
from discord.ext import commands
from bs4 import BeautifulSoup as Soup
from modules.tryget import tryget
from modules.steamapp import SteamApp
from modules.embed import *


class Sub:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='sub')
    @commands.has_permissions(manage_channels=True)
    async def sub(self, ctx, *args):
        searchurl = 'https://store.steampowered.com/search/?term='
        keyword = ""
        for arg in args:
            keyword = keyword + " " + arg
            searchurl = searchurl + f'{arg}+'
        searchurl = searchurl[:-1]
        result = await tryget(searchurl)
        resultpage = Soup(result, 'html.parser')
        top5 = [title for title in resultpage('span', {'class': 'title'})[0:5]]
        message = embed(f"Searching for {keyword}", "The following search results were found...")
        commandlist = []
        for entry in top5:
            place = top5.index(entry) + 1
            message.add_field(name=f"Entry #{place}", value=entry.text, inline=False)
            commandlist.append(f'{place}\u20e3')
        decision = await launch(message, ctx, self.bot, 30.0, commandlist)
        entry = top5[int(decision[0]) - 1]
        name = entry.text
        appid = entry.parent.parent.parent['data-ds-appid']
        with open('json/steam.json') as steam:
            steamdict = json.load(steam)
        if appid not in steamdict:
            with open('json/name.json') as namefile:
                namedict = json.load(namefile)
            namedict[appid] = name
            with open('json/name.json', 'w') as newname:
                json.dump(namedict, newname)
            steamdict[appid] = []
            ng = SteamApp(appid, self.bot)
            ng.fetchname()
            await ng.parse()
            await ng.gaben()
            with open('json/update.json') as update:
                updatedict = json.load(update)
            updatedict[appid] = ng.found
            with open('json/update.json', 'w') as newupdate:
                json.dump(updatedict, newupdate)
            with open('json/sale.json') as sale:
                saledict = json.load(sale)
            saledict[appid] = ng.foundsale
            with open('json/sale.json', 'w') as newsale:
                json.dump(saledict, newsale)
            with open('json/subbed.json') as subbed:
                subbeddict = json.load(subbed)
            if ctx.message.channel.id not in subbeddict:
                subbeddict[ctx.message.channel.id] = []
            subbeddict[ctx.message.channel.id].append(appid)
            with open('json/subbed.json', 'w') as newsubbed:
                json.dump(subbeddict, newsubbed)
        if ctx.message.channel.id in steamdict[appid]:
            unsuccessful = embed("Unsuccessful.", f"This channel is already subscribed to {name}.")
            await launch(unsuccessful, ctx, self.bot)
        else:
            steamdict[appid].append(ctx.message.channel.id)
            with open('json/steam.json', 'w') as newsteam:
                json.dump(steamdict, newsteam)
            success = embed("Success!", f"This channel is now subscribed to {name}!")
            await launch(success, ctx, self.bot)

    # @commands.command(name='subbed')
    # @commands.has_permissions(manage_channels=True)
    # async def subbed(self, ctx):



def setup(bot):
    bot.add_cog(Sub(bot))
