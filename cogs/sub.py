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
        entrylist = [entry.text for entry in top5]
        message = Embed(f"Searching for {keyword}.", "The following search results were found...", self.bot, ctx)
        message.prepare(entrylist)
        decision = await message.launchspecial()
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
            if str(ctx.message.channel.id) not in subbeddict:
                subbeddict[str(ctx.message.channel.id)] = []
            subbeddict[str(ctx.message.channel.id)].append(appid)
            with open('json/subbed.json', 'w') as newsubbed:
                json.dump(subbeddict, newsubbed)
        if ctx.message.channel.id in steamdict[appid]:
            unsuccessful = Embed("Unsuccessful.", f"This channel is already subscribed to {name}.", self.bot, ctx)
            await unsuccessful.launchnormal()
        else:
            steamdict[appid].append(ctx.message.channel.id)
            with open('json/steam.json', 'w') as newsteam:
                json.dump(steamdict, newsteam)
            success = Embed("Success!", f"This channel is now subscribed to {name}!", self.bot, ctx)
            await success.launchnormal()

    @commands.command(name='subbed')
    @commands.has_permissions(manage_channels=True)
    async def subbed(self, ctx):
        channelid = ctx.message.channel.id
        with open('json/subbed.json') as subbed:
            subbeddict = json.load(subbed)
        with open('json/name.json') as name:
            namedict = json.load(name)
        namelist = [namedict[appid] for appid in subbeddict[str(channelid)]]
        idlist = [appid for appid in subbeddict[str(channelid)]]
        message = Embed(f"Searching for {self.bot.get_channel(channelid)}'s subscribed games.",
                        "The following search results were found...", self.bot, ctx)
        message.prepare(namelist)
        resulttup = await message.launchspecial()
        appid = idlist[int(resulttup[1][0]) - 1 + resulttup[0] * 9]
        print(appid)


def setup(bot):
    bot.add_cog(Sub(bot))